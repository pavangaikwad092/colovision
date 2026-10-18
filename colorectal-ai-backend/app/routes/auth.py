from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Admin, User
from ..schemas import LoginIn, RegisterIn, TokenOut
from ..services.authentication import create_token, hash_password, verify_password
router = APIRouter(prefix="/api/auth", tags=["authentication"])
@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(or_(User.email == data.email, User.username == data.username)).first(): raise HTTPException(409, "Email or username already exists")
    db.add(User(**data.model_dump(exclude={"password"}), password_hash=hash_password(data.password))); db.commit()
    return {"message": "Registration submitted and waiting for administrator approval."}
@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(or_(User.email == data.identifier, User.username == data.identifier)).first()
    if not user or not verify_password(data.password, user.password_hash): raise HTTPException(401, "Invalid login credentials")
    if user.status != "APPROVED": raise HTTPException(403, f"Account status: {user.status}")
    return {"access_token": create_token(user.id, "user")}
@router.post("/admin/login", response_model=TokenOut)
def admin_login(data: LoginIn, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == data.identifier).first()
    if not admin or not verify_password(data.password, admin.password_hash): raise HTTPException(401, "Invalid administrator credentials")
    return {"access_token": create_token(admin.id, "admin")}
