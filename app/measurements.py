
import math
import zipfile
from datetime import date, datetime
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import mapping


def to_json_safe(value):
    """Convert values to JSON-compatible Python values."""
    if value is None or value is pd.NaT:
        return None

    if isinstance(value, np.generic):
        value = value.item()

    if value is None:
        return None

    if isinstance(value, (datetime, date, pd.Timestamp)):
        if pd.isna(value):
            return None
        return value.isoformat()

    if isinstance(value, float):
        return value if math.isfinite(value) else None

    if isinstance(value, dict):
        return {
            str(key): to_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [to_json_safe(item) for item in value]

    if isinstance(value, (str, int, bool)):
        return value

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    return str(value)


def read_geospatial_file(file_path: Path) -> gpd.GeoDataFrame:
    """Read a KML file or combine Shapefiles from a ZIP archive."""
    extension = file_path.suffix.lower()

    if extension == ".kml":
        return gpd.read_file(file_path, driver="KML")

    if extension == ".zip":
        with zipfile.ZipFile(file_path, "r") as archive:
            shp_files = [
                name
                for name in archive.namelist()
                if name.lower().endswith(".shp")
                and not name.startswith("__MACOSX/")
                and not Path(name).name.startswith("._")
            ]

        if not shp_files:
            raise ValueError(
                "The ZIP archive does not contain any Shapefiles"
            )

        frames = []

        for shp_file in shp_files:
            layer = gpd.read_file(
                f"zip://{file_path.resolve()}!{shp_file}"
            )

            if layer.empty:
                continue

            if layer.crs is None:
                raise ValueError(
                    f"The Shapefile '{shp_file}' has no CRS information"
                )

            frames.append(layer)

        if not frames:
            raise ValueError(
                "The ZIP archive contains no geographic features"
            )

        # Reproject layers to a common CRS before combining them.
        target_crs = frames[0].crs
        normalized_frames = [
            frame.to_crs(target_crs)
            for frame in frames
        ]

        combined = pd.concat(
            normalized_frames,
            ignore_index=True,
        )

        return gpd.GeoDataFrame(
            combined,
            geometry="geometry",
            crs=target_crs,
        )

    raise ValueError("Unsupported file format. Use .kml or .zip")


def calculate_measurements(file_path: Path) -> list[dict]:
    """Extract feature details, coordinates, and measurements."""
    gdf = read_geospatial_file(file_path)

    if gdf.empty:
        raise ValueError("The file contains no geographic features")

    if gdf.crs is None:
        raise ValueError(
            "The file has no CRS information. A valid CRS is required."
        )

    # Estimate a projected CRS suitable for metric measurements.
    projected_crs = gdf.estimate_utm_crs()

    if projected_crs is None:
        raise ValueError(
            "Could not determine a suitable projected CRS"
        )

    projected_gdf = gdf.to_crs(projected_crs)
    results = []

    for position, (index, row) in enumerate(gdf.iterrows()):
        geometry = row.geometry

        geometry_type = (
            geometry.geom_type
            if geometry is not None
            else None
        )

        geometry_data = None
        area_m2 = None
        length_m = None

        if geometry is not None and not geometry.is_empty:
            # Preserve original coordinates in the response.
            geometry_data = to_json_safe(mapping(geometry))

            # Use projected coordinates for measurements.
            projected_geometry = projected_gdf.geometry.iloc[position]

            if (
                projected_geometry is not None
                and not projected_geometry.is_empty
            ):
                if geometry_type in ("Polygon", "MultiPolygon"):
                    area_m2 = float(projected_geometry.area)

                elif geometry_type in (
                    "LineString",
                    "MultiLineString",
                ):
                    length_m = float(projected_geometry.length)

        properties = {
            str(key): to_json_safe(value)
            for key, value in row.items()
            if key != gdf.geometry.name
        }

        results.append({
            "feature_id": str(index),
            "geometry_type": geometry_type,
            "geometry": geometry_data,
            "crs": str(gdf.crs),
            "measurement_crs": str(projected_crs),
            "properties": properties,
            "area_m2": area_m2,
            "length_m": length_m,
        })

    return results
