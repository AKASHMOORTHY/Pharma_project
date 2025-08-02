from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app import models, schemas
from typing import List
from app.dependencies import role_required

router = APIRouter(prefix="/api/dashboard/anomalies", tags=["Anomalies"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schemas.AnomalyOut], dependencies=[Depends(role_required(["Manager", "QA"]))])
def get_anomaly_dashboard(db: Session = Depends(get_db)):
    return db.query(models.Anomaly).all()

