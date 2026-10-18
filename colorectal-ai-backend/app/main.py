from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import Base, engine
from .routes import admin, auth, patients, prediction, reports
from .services.classification import load_classification_model
from .services.segmentation import load_segmentation_model

app = FastAPI(title="ColoVision AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(patients.router)
app.include_router(prediction.router)
app.include_router(reports.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    settings.models_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    load_segmentation_model()
    load_classification_model()


@app.get("/health")
def health():
    return {"status": "ok"}
