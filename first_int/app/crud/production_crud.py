from sqlalchemy.orm import Session
from app.models.production_models import ProductionBatch, StageLog, ProcessStage
from app.schemas.production_schemas import ProductionBatchCreate, StageLogCreate, StageLogUpdate, ProcessStageCreate, ProcessStageResponse, ProductionBatchResponse, ProcessStageCreate
from fastapi import HTTPException
from typing import List

def create_batch(db: Session, batch: dict):
    db_batch = ProductionBatch(**batch)
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch

def create_stage_log(db: Session, log: StageLogCreate):
    db_log = StageLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def update_stage_log(db: Session, log_id: int, updated_data: StageLogUpdate):
    log = db.query(StageLog).filter(StageLog.id == log_id).first()

    if not log:
        raise HTTPException(status_code=404, detail="Stage log not found")

    # 🔒 Check if locked
    if log.is_locked == 1:
        raise HTTPException(
            status_code=403,
            detail="This log is locked and cannot be modified. Manager override required."
        )

    # ✅ Proceed with update if not locked
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(log, key, value)

    db.commit()
    db.refresh(log)
    return log

def get_stage_logs_by_batch(db: Session, batch_code: str) -> List[StageLog]:
    return (
        db.query(StageLog)
        .join(ProductionBatch)
        .filter(ProductionBatch.batch_code == batch_code)
        .all()
    )

def get_all_batches(db: Session):
    return db.query(ProductionBatch).all()

def create_process_stage(db: Session, stage: ProcessStageCreate):
    db_stage = ProcessStage(**stage.dict())
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage

def get_all_process_stages(db: Session):
    return db.query(ProcessStage).all()
