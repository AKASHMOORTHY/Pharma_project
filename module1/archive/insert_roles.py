# insert_roles.py
from module1.database import SessionLocal
from module1.models.role import Role

# Predefined roles
roles = [
    {"name": "Admin", "description": "System administrator with full access"},
    {"name": "Manager", "description": "Plant or process manager"},
    {"name": "Supervisor", "description": "Shift/line supervisor"},
    {"name": "QA", "description": "Quality analyst for checking logs"},
]

# Start session
db = SessionLocal()

for role_data in roles:
    existing = db.query(Role).filter_by(name=role_data["name"]).first()
    if not existing:
        role = Role(**role_data)
        db.add(role)

db.commit()
db.close()

print("Default roles inserted.")
