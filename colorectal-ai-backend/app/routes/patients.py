from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Patient
from ..schemas import PatientIn
from ..services.authentication import current_user
router = APIRouter(prefix="/api/patients", tags=["patients"])
@router.post("")
def create(data: PatientIn, db: Session = Depends(get_db), user=Depends(current_user)):
    if db.query(Patient).filter(Patient.patient_id == data.patient_id).first(): raise HTTPException(409, "Patient ID already exists")
    patient = Patient(**data.model_dump(), created_by=user.id); db.add(patient); db.commit(); db.refresh(patient); return patient
@router.get("")
def all_patients(db: Session = Depends(get_db), user=Depends(current_user)): return db.query(Patient).filter(Patient.created_by == user.id).all()
@router.get("/{patient_id}")
def detail(patient_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    patient = db.get(Patient, patient_id)
    if not patient or patient.created_by != user.id: raise HTTPException(404, "Patient not found")
    return patient
