from app.database import SessionLocal
from app.models import Admin
from app.services.authentication import hash_password

db = SessionLocal()

admin = Admin(
    name="Administrator",
    email="admin@colovision.com",
    password_hash=hash_password("admin123")
)

db.add(admin)
db.commit()

print("Admin created successfully.")
print("Email: admin@colovision.com")
print("Password: admin123")

db.close()