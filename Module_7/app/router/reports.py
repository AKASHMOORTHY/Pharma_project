from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.tasks import report_tasks
from app.dependencies import role_required
import os
from typing import Optional
import uuid
from app.tasks.report_tasks import generate_report
from pydantic import BaseModel

router = APIRouter(prefix="/api/reports", tags=["Reports"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ReportRequest(BaseModel):
    report_name: str
    format: str = "pdf"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
# @router.post("/custom", dependencies=[Depends(role_required(["Manager"]))])
# def generate_custom_report(
#     report_name: str,
#     format: str = "pdf",
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
# ):
#     task = report_tasks.generate_report.delay(report_name, format, start_date, end_date)

@router.post("/custom", dependencies=[Depends(role_required(["Manager"]))])
def generate_custom_report(request: ReportRequest):
    task = report_tasks.generate_report.delay(
        request.report_name, request.format, request.start_date, request.end_date
    )
    return {"task_id": task.id, "status": "Report generation started"}

@router.get("/download/{file_name}", dependencies=[Depends(role_required(["Manager"]))])
def download_report(file_name: str):
    file_path = f"generated_reports/{file_name}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=file_name)
    return JSONResponse(content={"error": "File not found"}, status_code=404)

@router.get("/generate")
def trigger_report(report_name: str = "QC Test", format: str = "pdf"):
    result = generate_report.delay(report_name, format)
    return {"task_id": result.id, "status": "task submitted"}