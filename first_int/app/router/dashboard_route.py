from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import SessionLocal
from app.models.dashboard_models import DashboardProductionBatch, QualityCheck, Inventory, Anomaly
from app.schemas.dashboard_schemas import ProductionOut, QCOut, InventoryOut, AnomalyOut, ReportRequest
from app.crud.dashboard_crud import populate_dashboard_anomaly, populate_dashboard_inventory, populate_dashboard_production, populate_dashboard_quality_check 
from app.tasks import report_tasks
from typing import List, Optional
from app.dependencies import role_required
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def starting(db:Session = Depends(get_db)):
    populate_dashboard_anomaly(db)
    populate_dashboard_inventory(db)
    populate_dashboard_production(db)
    populate_dashboard_quality_check(db)
    return "Successfully Updated"

#anomalies
@router.get("/anomalies", response_model=List[AnomalyOut], dependencies=[Depends(role_required(["Manager", "QA"]))])
def get_anomaly_dashboard(db: Session = Depends(get_db)):
#    populate_dashboard_anomaly(db)
   return db.query(Anomaly).all()

#inventory

@router.get("/inventory", response_model=List[InventoryOut], dependencies=[Depends(role_required(["Manager", "Storekeeper"]))])
def get_inventory_dashboard(db: Session = Depends(get_db)):
   
   return db.query(Inventory).all()


@router.get("/inventory/stats", dependencies=[Depends(role_required(["Manager", "Storekeeper"]))])
def get_inventory_stats(db: Session = Depends(get_db)):

    recent_cutoff = datetime.now() - timedelta(days=7)

    fast_moving = db.query(Inventory).filter(Inventory.updated_at >= recent_cutoff).count()
    slow_moving = db.query(Inventory).filter(Inventory.updated_at < recent_cutoff).count()
    reorder_alerts = db.query(Inventory).filter(Inventory.quantity < 100).count()  # threshold

    return {
        "fast_moving": fast_moving,
        "slow_moving": slow_moving,
        "reorder_alerts": reorder_alerts
    }

# production

@router.get("/production", dependencies=[Depends(role_required(["Manager", "Supervisor"]))])
def get_production_dashboard(
    db: Session = Depends(get_db),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    shift: Optional[str] = None
   ):

    query = db.query(
        func.date(DashboardProductionBatch.production_date).label("date"),
        DashboardProductionBatch.shift,
        func.count().label("total_batches"),
        func.sum(case((DashboardProductionBatch.status == 'Completed', 1), else_=0)).label("completed_batches"),
        func.avg(DashboardProductionBatch.duration).label("avg_batch_time")
    )

    if start_date:
        query = query.filter(DashboardProductionBatch.production_date >= start_date)
    if end_date:
        query = query.filter(DashboardProductionBatch.production_date <= end_date)
    if shift:
        query = query.filter(DashboardProductionBatch.shift == shift)

    data = query.group_by(
        func.date(DashboardProductionBatch.production_date),
        DashboardProductionBatch.shift
    ).all()

    return [ProductionOut.model_validate(row) for row in data]


@router.get("/production/kpis", dependencies=[Depends(role_required(["Manager"]))])
def get_production_kpis(db: Session = Depends(get_db)):

    return {
        "today_batches": db.query(func.count(DashboardProductionBatch.id))
                          .filter(func.date(DashboardProductionBatch.production_date) == func.current_date()-timedelta(days=3))
                          .scalar(),
        "weekly_efficiency": calculate_weekly_efficiency(db),
        "qc_rejection_percent": calculate_qc_rejection_rate(db),
        "avg_anomaly_resolution_time_hr": calculate_avg_resolution_time(db)
    }

def calculate_weekly_efficiency(db: Session):    
 
    completed = db.query(func.count(DashboardProductionBatch.id)).filter(
        DashboardProductionBatch.status == 'Completed',
        func.date(DashboardProductionBatch.production_date) >= func.current_date() - timedelta(days=30)
    ).scalar()
    total = db.query(func.count(DashboardProductionBatch.id)).filter(
        func.date(DashboardProductionBatch.production_date) >= func.current_date() - timedelta(days=30)
    ).scalar()
    return (completed / total) * 100 if total else 0

def calculate_qc_rejection_rate(db: Session):

    total = db.query(func.count(QualityCheck.id)).scalar()
    failed = db.query(func.count(QualityCheck.id)).filter(QualityCheck.result == "Fail").scalar()
    return (failed / total) * 100 if total else 0

def calculate_avg_resolution_time(db: Session):

    anomalies = db.query(Anomaly).filter(Anomaly.resolved_at.isnot(None)).all()
    if not anomalies:
        return 0
    total_time = sum([(a.resolved_at - a.created_at).total_seconds() for a in anomalies])
    avg_time = total_time / len(anomalies)
    return round(avg_time / 3600, 2)  # in hours

#qc

@router.get("/qc", response_model=List[QCOut], dependencies=[Depends(role_required(["Manager", "QA"]))])
def get_qc_dashboard(db: Session = Depends(get_db)):
    
    return db.query(QualityCheck).all()


# reports
@router.post("/report/custom", dependencies=[Depends(role_required(["Manager"]))])
def generate_custom_report(request: ReportRequest):
    task = report_tasks.generate_report.delay(
        request.report_name, request.format, request.start_date, request.end_date, request.shift
    )
    return {"task_id": task.id, "status": "Report generation started"}

@router.get("/report/download/{file_name}", dependencies=[Depends(role_required(["Manager"]))])
def download_report(file_name: str):
    file_path = f"generated_reports/{file_name}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=file_name)
    return JSONResponse(content={"error": "File not found"}, status_code=404)

@router.get("/report/generate")
def trigger_report(report_name: str = "QC Test", format: str = "pdf"):
    result = report_tasks.generate_report.delay(report_name, format)
    return {"task_id": result.id, "status": "task submitted"}

@router.get("/report/anomaly")
def trigger_anomaly_report():
    result = report_tasks.generate_anomaly_report.delay()
    return {"task_id": result.id, "status": "Anomaly report generation started"}

