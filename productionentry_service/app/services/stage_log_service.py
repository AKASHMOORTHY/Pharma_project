from sqlalchemy.orm import Session
from models.stage_log import StageLog
from schemas.stage_log_schema import StageLogCreate
from fastapi import HTTPException

def create_stage_log(db: Session, log: StageLogCreate):
    if log.start_time >= log.end_time:
        raise HTTPException(status_code=400, detail="End time must be after start time.")
    if log.input_quantity < log.output_quantity:
        raise HTTPException(status_code=400, detail="Output cannot exceed input.")

    new_log = StageLog(**log.dict())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

def list_stage_logs_by_batch(db: Session, batch_id: int):
    return db.query(StageLog).filter(StageLog.production_batch_id == batch_id).all()
