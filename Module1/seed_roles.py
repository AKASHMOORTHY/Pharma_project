# seed_roles.py
from user_management.app.database import SessionLocal
from user_management.app.models import Role

db = SessionLocal()

roles = ["Admin", "Supervisor", "QA", "Manager"]
for role_name in roles:
    existing = db.query(Role).filter_by(name=role_name).first()
    if not existing:
        db.add(Role(name=role_name))

db.commit()
db.close()
print("✅ Roles seeded successfully.")
