from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4, UUID
import shutil

from app.measurements import calculate_measurements

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = (".zip", ".kml")


@router.post("/api/files/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail="Only .zip and .kml files are allowed"
        )

    file_id = str(uuid4())
    extension = Path(file.filename).suffix.lower()
    saved_path = UPLOAD_DIR / f"{file_id}{extension}"

    try:
        with saved_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        await file.close()

    return {
        "id": file_id,
        "filename": file.filename,
        "message": "File uploaded and saved successfully"
    }


@router.get("/api/files/{file_id}/")
async def get_file_details(file_id: UUID):
    matching_files = list(UPLOAD_DIR.glob(f"{file_id}.*"))

    if not matching_files:
        raise HTTPException(status_code=404, detail="File not found")

    saved_file = matching_files[0]

    return {
        "id": str(file_id),
        "stored_filename": saved_file.name,
        "extension": saved_file.suffix.lower(),
        "message": "File exists"
    }


@router.get("/api/files/{file_id}/measurements/")
async def get_measurements(file_id: UUID):
    matching_files = list(UPLOAD_DIR.glob(f"{file_id}.*"))

    if not matching_files:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        measurements = calculate_measurements(matching_files[0])

        return {
            "file_id": str(file_id),
            "count": len(measurements),
            "measurements": measurements
        }

    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Could not process geospatial file: {exc}"
        )