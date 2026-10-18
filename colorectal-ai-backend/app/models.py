from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120)); email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255)); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120)); email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str] = mapped_column(String(30)); username: Mapped[str] = mapped_column(String(80), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255)); status: Mapped[str] = mapped_column(String(20), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow); approved_by: Mapped[int | None] = mapped_column(ForeignKey("admins.id")); approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
class Patient(Base):
    __tablename__ = "patients"
    id: Mapped[int] = mapped_column(primary_key=True); patient_id: Mapped[str] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(120)); address: Mapped[str] = mapped_column(Text); age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(20)); contact: Mapped[str] = mapped_column(String(30)); photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id")); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    predictions: Mapped[list["Prediction"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(primary_key=True); patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    image_path: Mapped[str] = mapped_column(String(500)); segmentation_path: Mapped[str] = mapped_column(String(500)); overlay_path: Mapped[str] = mapped_column(String(500))
    predicted_class: Mapped[str] = mapped_column(String(80)); confidence: Mapped[float] = mapped_column(Float)
    adenocarcinoma_probability: Mapped[float] = mapped_column(Float); high_grade_probability: Mapped[float] = mapped_column(Float); low_grade_probability: Mapped[float] = mapped_column(Float); normal_probability: Mapped[float] = mapped_column(Float); polyp_probability: Mapped[float] = mapped_column(Float); serrated_probability: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow); patient: Mapped[Patient] = relationship(back_populates="predictions")
class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True); patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id")); prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"), unique=True)
    report_path: Mapped[str] = mapped_column(String(500)); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
