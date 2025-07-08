from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services import production_batch_service, stage_log_service
from schemas import production_batch_schema, stage_log_schema
from dependencies import get_db

router = APIRouter(
    prefix="/production",
    tags=["Production"]
)

@router.post("/batch/", response_model=production_batch_schema.ProductionBatchOut)
def create_batch(batch: production_batch_schema.ProductionBatchCreate, db: Session = Depends(get_db)):
    return production_batch_service.create_batch(db, batch)

@router.get("/batch/", response_model=list[production_batch_schema.ProductionBatchOut])
def list_batches(db: Session = Depends(get_db)):
    return production_batch_service.list_batches(db)

@router.post("/stage-log/", response_model=stage_log_schema.StageLogOut)
def create_stage_log(log: stage_log_schema.StageLogCreate, db: Session = Depends(get_db)):
    return stage_log_service.create_stage_log(db, log)

@router.get("/stage-log/batch/{batch_id}", response_model=list[stage_log_schema.StageLogOut])
def list_logs(batch_id: int, db: Session = Depends(get_db)):
    return stage_log_service.list_stage_logs_by_batch(db, batch_id)
