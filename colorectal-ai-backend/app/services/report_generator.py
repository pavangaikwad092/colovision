from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas
def generate_report(path: Path, patient, prediction):
    c = Canvas(str(path), pagesize=A4); y = 800
    for line in ["COLORECTAL CANCER DETECTION", "DEEP LEARNING ANALYSIS REPORT", "", f"Patient ID: {patient.patient_id}", f"Patient: {patient.name}", f"Age / Gender: {patient.age} / {patient.gender}", f"Analysis: {prediction.created_at}", "", f"Predicted Tissue Class: {prediction.predicted_class}", f"Confidence: {prediction.confidence:.2%}", "", "Research and decision-support use only. Not a definitive medical diagnosis."]:
        c.drawString(50, y, line); y -= 25
    c.save()
