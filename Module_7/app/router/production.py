
from fastapi import APIRouter, Depends
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from typing import List, Optional
from app.dependencies import role_required

router = APIRouter(prefix="/api/dashboard/production", tags=["Production"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", dependencies=[Depends(role_required(["Manager", "Supervisor"]))])
def get_production_dashboard(
    db: Session = Depends(get_db),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    shift: Optional[str] = None
):
    query = db.query(
        func.date(models.ProductionBatch.production_date).label("date"),
        models.ProductionBatch.shift,
        func.count().label("total_batches"),
        func.sum(case((models.ProductionBatch.status == 'Completed', 1), else_=0)).label("completed_batches"),
        func.avg(models.ProductionBatch.duration).label("avg_batch_time")
    )

    if start_date:
        query = query.filter(models.ProductionBatch.production_date >= start_date)
    if end_date:
        query = query.filter(models.ProductionBatch.production_date <= end_date)
    if shift:
        query = query.filter(models.ProductionBatch.shift == shift)

    data = query.group_by(
        func.date(models.ProductionBatch.production_date),
        models.ProductionBatch.shift
    ).all()

    return [schemas.ProductionOut.model_validate(row) for row in data]

""" @router.get("/", response_model=List[schemas.ProductionOut], dependencies=[Depends(role_required(["Manager", "Supervisor"]))])
def get_production_dashboard(db: Session = Depends(get_db)):
    data = (
        db.query(
            func.date(models.ProductionBatch.production_date).label("date"),
            models.ProductionBatch.shift,
            func.count().label("total_batches"),
            func.sum(case((models.ProductionBatch.status == 'Completed', 1), else_=0)).label("completed_batches"),
            func.avg(models.ProductionBatch.duration).label("avg_batch_time")
        )
        .group_by(func.date(models.ProductionBatch.production_date), models.ProductionBatch.shift)
        .all()
    )
    print("DEBUG: production dashboard data:", data)
    return [schemas.ProductionOut.model_validate(row) for row in data] """

@router.get("/kpis", dependencies=[Depends(role_required(["Manager"]))])
def get_production_kpis(db: Session = Depends(get_db)):
    return {
        "today_batches": db.query(func.count(models.ProductionBatch.id))
                          .filter(func.date(models.ProductionBatch.production_date) == func.current_date())
                          .scalar(),
        "weekly_efficiency": calculate_weekly_efficiency(db),
        "qc_rejection_percent": calculate_qc_rejection_rate(db),
        "avg_anomaly_resolution_time_hr": calculate_avg_resolution_time(db)
    }

def calculate_weekly_efficiency(db: Session):
    completed = db.query(func.count(models.ProductionBatch.id)).filter(
        models.ProductionBatch.status == 'Completed',
        func.date(models.ProductionBatch.production_date) >= func.date('now', '-7 days')
    ).scalar()
    total = db.query(func.count(models.ProductionBatch.id)).filter(
        func.date(models.ProductionBatch.production_date) >= func.date('now', '-7 days')
    ).scalar()
    return (completed / total) * 100 if total else 0

def calculate_qc_rejection_rate(db: Session):
    total = db.query(func.count(models.QualityCheck.id)).scalar()
    failed = db.query(func.count(models.QualityCheck.id)).filter(models.QualityCheck.result == "Fail").scalar()
    return (failed / total) * 100 if total else 0

def calculate_avg_resolution_time(db: Session):
    anomalies = db.query(models.Anomaly).filter(models.Anomaly.resolved_at.isnot(None)).all()
    if not anomalies:
        return 0
    total_time = sum([(a.resolved_at - a.created_at).total_seconds() for a in anomalies])
    avg_time = total_time / len(anomalies)
    return round(avg_time / 3600, 2)  # in hours
