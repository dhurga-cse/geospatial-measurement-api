
from pathlib import Path
import zipfile

import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point

output_dir = Path("test_shapefile")
output_dir.mkdir(exist_ok=True)

features = {
    "polygons": [
        Polygon([
            (76.9558, 11.0168),
            (76.9568, 11.0168),
            (76.9568, 11.0178),
            (76.9558, 11.0178),
            (76.9558, 11.0168),
        ])
    ],
    "lines": [
        LineString([
            (76.9558, 11.0168),
            (76.9568, 11.0168),
        ])
    ],
    "points": [Point(76.9563, 11.0173)],
}

for name, geometries in features.items():
    gdf = gpd.GeoDataFrame(
        {"Name": [f"Test {name.title()}"]},
        geometry=geometries,
        crs="EPSG:4326",
    )
    gdf.to_file(
        output_dir / f"{name}.shp",
        driver="ESRI Shapefile",
    )

zip_path = Path("sample-shapefiles.zip")

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in output_dir.iterdir():
        if path.is_file():
            archive.write(path, arcname=path.name)

print(f"Created test archive: {zip_path.resolve()}")
