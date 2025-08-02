from app.database import SessionLocal
from app import models
from datetime import datetime, timedelta
import random

db = SessionLocal()

# Clear existing data
db.query(models.ProductionBatch).delete()
db.query(models.QualityCheck).delete()
db.query(models.Inventory).delete()
db.query(models.Anomaly).delete()

# Production Batches
shifts = ['A', 'B', 'C']
for i in range(10):
    batch = models.ProductionBatch(
        production_date=datetime.now().date() - timedelta(days=i),
        shift=random.choice(shifts),
        status=random.choice(['Completed', 'Pending']),
        duration=random.randint(20, 60)
    )
    db.add(batch)

# QC Checks
for _ in range(10):
    qc = models.QualityCheck(
        result=random.choice(['Pass', 'Fail']),
        reason=random.choice(['Moisture High', 'Impurities Found', 'Color Mismatch', None]),
        created_at=datetime.now() - timedelta(days=random.randint(0, 5))
    )
    db.add(qc)

# Inventory
categories = ['Raw', 'Packing']
for _ in range(10):
    inv = models.Inventory(
        material=f'Material {_}',
        quantity=random.randint(100, 500),
        category=random.choice(categories),
        location=f'Warehouse {_}',
        updated_at=datetime.now()
    )
    db.add(inv)

# Anomalies
for _ in range(5):
    anomaly = models.Anomaly(
        category=random.choice(['Equipment', 'Quality', 'Temperature']),
        status=random.choice(['Open', 'Resolved']),
        created_at=datetime.now() - timedelta(days=random.randint(1, 7)),
        resolved_at=None if random.random() < 0.5 else datetime.now()
    )
    db.add(anomaly)

db.commit()
db.close()

print("✅ Dummy data inserted")
