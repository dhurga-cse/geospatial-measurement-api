from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="Geospatial File Measurement API",
    description="An API to upload geospatial files and calculate measurements.",
    version="1.0.0"
)
app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "Geospatial File Measurement API is running",
        "status": "success"
    }


@app.get("/api/health/")
def health_check():
    return {"status": "healthy"}