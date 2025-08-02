from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from typing import List
from app.dependencies import role_required

router = APIRouter(prefix="/api/dashboard/inventory", tags=["Inventory"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.InventoryOut], dependencies=[Depends(role_required(["Manager", "Storekeeper"]))])
def get_inventory_dashboard(db: Session = Depends(get_db)):
    return db.query(models.Inventory).all()

from datetime import datetime, timedelta

@router.get("/stats", dependencies=[Depends(role_required(["Manager", "Storekeeper"]))])
def get_inventory_stats(db: Session = Depends(get_db)):
    recent_cutoff = datetime.now() - timedelta(days=7)

    fast_moving = db.query(models.Inventory).filter(models.Inventory.updated_at >= recent_cutoff).count()
    slow_moving = db.query(models.Inventory).filter(models.Inventory.updated_at < recent_cutoff).count()
    reorder_alerts = db.query(models.Inventory).filter(models.Inventory.quantity < 100).count()  # threshold

    return {
        "fast_moving": fast_moving,
        "slow_moving": slow_moving,
        "reorder_alerts": reorder_alerts
    }
