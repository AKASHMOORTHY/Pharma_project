# app/routers/stage_log.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app import schemas, crud
from app.schemas import StageLogResponse
from app.dependencies import get_db

router = APIRouter()

@router.post("/")
def create_stage(
    log: schemas.StageLogCreate,
    db: Session = Depends(get_db)
):
    return crud.create_stage_log(db, log)

@router.put("/{log_id}")
def update_stage(
    log_id: int,
    log: schemas.StageLogUpdate,
    db: Session = Depends(get_db)
):
    return crud.update_stage_log(db, log_id, log)

@router.get("/batch/{batch_code}/", response_model=List[StageLogResponse])
def get_logs_by_batch(
    batch_code: str,
    db: Session = Depends(get_db)
):
    return crud.get_stage_logs_by_batch(db, batch_code)
