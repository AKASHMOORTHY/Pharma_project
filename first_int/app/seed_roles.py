# seed_roles.py
import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.database import SessionLocal
from app.models.user_models import Role

db = SessionLocal()

roles = ["Admin", "Supervisor", "QA", "Manager", "Vendor", "Storekeeper"]
for role_name in roles:
    existing = db.query(Role).filter_by(name=role_name).first()
    if not existing:
        db.add(Role(name=role_name))

db.commit()
db.close()
print("✅ Roles seeded successfully.")

