from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..services.authentication import current_admin
router = APIRouter(prefix="/api/admin", tags=["admin"])
@router.get("/users/pending")
def pending(db: Session = Depends(get_db), admin=Depends(current_admin)): return db.query(User).filter(User.status == "PENDING").all()
def update(user_id: int, state: str, db: Session, admin):
    user = db.get(User, user_id)
    if not user: raise HTTPException(404, "User not found")
    user.status = state; user.approved_by = admin.id; user.approved_at = datetime.utcnow(); db.commit(); return {"message": f"User {state.lower()}"}
@router.put("/users/{user_id}/approve")
def approve(user_id: int, db: Session = Depends(get_db), admin=Depends(current_admin)): return update(user_id, "APPROVED", db, admin)
@router.put("/users/{user_id}/reject")
def reject(user_id: int, db: Session = Depends(get_db), admin=Depends(current_admin)): return update(user_id, "REJECTED", db, admin)
@router.put("/users/{user_id}/suspend")
def suspend(user_id: int, db: Session = Depends(get_db), admin=Depends(current_admin)): return update(user_id, "SUSPENDED", db, admin)
