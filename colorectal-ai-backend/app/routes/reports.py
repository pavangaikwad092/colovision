from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..models import Patient, Prediction, Report
from ..services.authentication import current_user
from ..services.report_generator import generate_report
router = APIRouter(prefix="/api/reports", tags=["reports"])
def get_prediction(prediction_id: int, db: Session, user):
    prediction = db.get(Prediction, prediction_id); patient = db.get(Patient, prediction.patient_id) if prediction else None
    if not prediction or not patient or patient.created_by != user.id: raise HTTPException(404, "Prediction not found")
    return prediction, patient
@router.get("/{prediction_id}")
def report(prediction_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    prediction, patient = get_prediction(prediction_id, db, user); saved = db.query(Report).filter(Report.prediction_id == prediction.id).first()
    if not saved:
        path = settings.upload_dir / "reports" / f"prediction_{prediction.id}.pdf"; path.parent.mkdir(parents=True, exist_ok=True); generate_report(path, patient, prediction)
        saved = Report(patient_id=patient.id, prediction_id=prediction.id, report_path=str(path)); db.add(saved); db.commit(); db.refresh(saved)
    return {"id": saved.id, "prediction_id": prediction.id, "report_path": saved.report_path}
@router.get("/{prediction_id}/download")
def download(prediction_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    prediction, patient = get_prediction(prediction_id, db, user); saved = db.query(Report).filter(Report.prediction_id == prediction.id).first()
    if not saved: report(prediction_id, db, user); saved = db.query(Report).filter(Report.prediction_id == prediction.id).first()
    return FileResponse(saved.report_path, media_type="application/pdf", filename=f"analysis_report_{prediction.id}.pdf")
