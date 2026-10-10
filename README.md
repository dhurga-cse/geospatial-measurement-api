# Geospatial File Measurement API

A REST API built using **FastAPI and GeoPandas** to upload geospatial files, extract geographic features, and calculate area and length measurements.

## Features

- Upload Shapefile ZIP archives (`.zip`) and KML files (`.kml`).
- Generate a unique ID for each uploaded file.
- Retrieve uploaded file details using the file ID.
- Extract feature IDs, geometry types, geometries, coordinate reference systems (CRS), and properties.
- Calculate polygon area in square metres (`m²`).
- Calculate line length in metres (`m`).
- Return `null` for measurements that do not apply, such as the area of a point.
- Reproject geographic data to a suitable projected CRS before calculating measurements.
- Return measurement results in JSON format.

## Technologies Used

- Python
- FastAPI
- GeoPandas
- Shapely
- PyProj
- Pyogrio
- Pandas
- NumPy
- Uvicorn

## Project Structure

```text
geospatial-measurement-api/
├── app/
│   ├── main.py
│   ├── routes.py
│   └── measurements.py
├── uploads/
├── .venv/
├── create_test_shapefile.py
├── sample-geospatial-test.kml
├── sample-shapefiles.zip
├── requirements.txt
├── .gitignore
└── README.md
```

The `uploads/` directory stores uploaded files. The `.venv/` directory contains the local Python virtual environment and should not be uploaded to GitHub.

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd geospatial-measurement-api
```

### 2. Create and activate a virtual environment

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the API server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

## API Endpoints

### 1. Health Check

**GET** `/api/health/`

Checks whether the API is running.

Example response:

```json
{
  "status": "healthy"
}
```

### 2. Upload a Geospatial File

**POST** `/api/files/`

Uploads a `.zip` Shapefile archive or `.kml` file.

Use multipart form data with the field name `file`.

Example response:

```json
{
  "id": "generated-file-uuid",
  "filename": "sample-geospatial-test.kml",
  "message": "File uploaded and saved successfully"
}
```

### 3. Get Uploaded File Details

**GET** `/api/files/{file_id}/`

Returns information about an uploaded file.

### 4. Get Feature Measurements

**GET** `/api/files/{file_id}/measurements/`

Returns the features and their calculated measurements.

Example response structure:

```json
{
  "file_id": "generated-file-uuid",
  "count": 1,
  "measurements": [
    {
      "feature_id": "0",
      "geometry_type": "Polygon",
      "geometry": {
        "type": "Polygon",
        "coordinates": []
      },
      "crs": "EPSG:4326",
      "measurement_crs": "EPSG:32643",
      "properties": {},
      "area_m2": 12092.12,
      "length_m": null
    }
  ]
}
```

The example values illustrate the response structure; actual values depend on the uploaded data.

## Testing the API

Open the interactive Swagger documentation:

`http://127.0.0.1:8000/docs`

Use Swagger UI to upload a KML or ZIP file, retrieve its file ID, and request measurements.

## Measurement Method

Geographic coordinates such as latitude and longitude are not directly suitable for calculating measurements in metres. The API reprojects the data to a suitable projected coordinate reference system before calculating polygon area and line length.

- **Polygon / MultiPolygon:** area in square metres.
- **LineString / MultiLineString:** length in metres.
- **Point / MultiPoint:** no area or length measurement.
- **Other geometry types:** measurement fields remain `null` unless supported by the implementation.

## Error Handling

The API returns appropriate HTTP errors for unsupported file extensions, missing files, and files that cannot be processed.

## License

This project was developed as a geospatial API assignment.
