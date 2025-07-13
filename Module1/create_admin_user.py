from user_management.app.database import SessionLocal
from user_management.app import models
from passlib.context import CryptContext

db = SessionLocal()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Check if 'Admin' role exists first
admin_role = db.query(models.Role).filter_by(name="Admin").first()
if not admin_role:
    admin_role = models.Role(name="Admin")
    db.add(admin_role)
    db.commit()
    db.refresh(admin_role)

# ✅ Check if admin user already exists
admin_email = "admin@example.com"
existing_user = db.query(models.User).filter_by(email=admin_email).first()
if not existing_user:
    admin_user = models.User(
        email=admin_email,
        full_name="Admin User",
        role_id=admin_role.id,
        shift="A",
        is_active=True,
        password=pwd_context.hash("admin123")  # use strong passwords in production
    )
    db.add(admin_user)
    db.commit()
    print("Admin user created successfully.")
else:
    print("Admin user already exists.")
