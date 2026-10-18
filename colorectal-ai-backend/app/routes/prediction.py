from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..models import Patient, Prediction
from ..services.authentication import current_user
from ..services.classification import predict_classification
from ..services.segmentation import predict_segmentation

router = APIRouter(prefix="/api", tags=["prediction"])
ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png"}


def save_upload(upload: UploadFile) -> Path:
    if upload.content_type not in ALLOWED:
        raise HTTPException(415, "Only JPG, JPEG, and PNG files are allowed")

    content = upload.file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, "Image is too large")

    try:
        Image.open(__import__("io").BytesIO(content)).verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(422, "Invalid image file")

    path = settings.upload_dir / "images" / f"{uuid4().hex}{ALLOWED[upload.content_type]}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def public_path(file_path: Path) -> str:
    return "/uploads/" + file_path.relative_to(settings.upload_dir).as_posix()


@router.post("/prediction")
def predict(
    patient_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient = db.get(Patient, patient_id)
    if not patient or patient.created_by != user.id:
        raise HTTPException(404, "Patient not found")

    image_path = save_upload(image)
    try:
        original = Image.open(image_path).convert("RGB")
        mask, overlay, classification_input = predict_segmentation(original)
        result = predict_classification(classification_input)

        output_dir = settings.upload_dir / "results"
        output_dir.mkdir(parents=True, exist_ok=True)

        mask_path = output_dir / f"{uuid4().hex}_mask.png"
        overlay_path = output_dir / f"{uuid4().hex}_overlay.png"
        mask.save(mask_path)
        overlay.save(overlay_path)

        public_mask = public_path(mask_path)
        public_overlay = public_path(overlay_path)
        public_image = public_path(image_path)

        p = result["probabilities"]
        row = Prediction(
            patient_id=patient.id,
            image_path=public_image,
            segmentation_path=public_mask,
            overlay_path=public_overlay,
            predicted_class=result["predicted_class"],
            confidence=result["confidence"],
            adenocarcinoma_probability=p[0],
            high_grade_probability=p[1],
            low_grade_probability=p[2],
            normal_probability=p[3],
            polyp_probability=p[4],
            serrated_probability=p[5],
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return {
            "id": row.id,
            **result,
            "mask_path": row.segmentation_path,
            "overlay_path": row.overlay_path,
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(500, "Prediction could not be completed")


@router.get("/predictions/{patient_id}")
def history(patient_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    patient = db.get(Patient, patient_id)
    if not patient or patient.created_by != user.id:
        raise HTTPException(404, "Patient not found")
    return patient.predictions
