import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.database import SessionLocal
from app.models import user_models
from passlib.context import CryptContext

db = SessionLocal()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Check if 'Admin' role exists first
admin_role = db.query(user_models.Role).filter_by(name="Admin").first()
if not admin_role:
    admin_role = user_models.Role(name="Admin")
    db.add(admin_role)
    db.commit()
    db.refresh(admin_role)

# ✅ Check if admin user already exists
admin_email = "admin@example.com"
existing_user = db.query(user_models.User).filter_by(email=admin_email).first()
if not existing_user:
    admin_user = user_models.User(
        email=admin_email,
        full_name="Admin User",
        role_id=admin_role.id,
        shift="A",
        is_active=True,
        hashed_password=pwd_context.hash("Admin@123")  # use strong passwords in production
    )
    db.add(admin_user)
    db.commit()
    print("Admin user created successfully.")
else:
    print("Admin user already exists.")
