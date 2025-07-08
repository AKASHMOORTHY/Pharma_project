from database import SessionLocal
from models import RawMaterial
from datetime import date

#create a new session
db = SessionLocal()

#create a sample raw material entry
sample_material = RawMaterial(
    name="Wood Pulp",
    unit="kg",
    opening_stock=1577.8,
    receipts=0.0,
    issues=0.0,
    closing_stock=1577.8,
    date=date(2025,12,3)
)

#Add it ti the session and commit

db.add(sample_material)
db.commit()
db.close()

print("sample raw material inserted successfully.")