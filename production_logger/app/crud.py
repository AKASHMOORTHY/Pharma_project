from sqlalchemy.orm import Session
from app import models, schemas

def create_batch(db: Session, batch: schemas.ProductionBatchCreate):
    db_batch = models.ProductionBatch(**batch.dict())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch

def create_stage_log(db: Session, log: schemas.StageLogCreate):
    db_log = models.StageLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def update_stage_log(db: Session, log_id: int, update: schemas.StageLogUpdate):
    log = db.query(models.StageLog).filter(models.StageLog.id == log_id).first()
    for k, v in update.dict().items():
        setattr(log, k, v)
    db.commit()
    db.refresh(log)
    return log



from typing import List

def get_stage_logs_by_batch(db: Session, batch_code: str) -> List[models.StageLog]:
    return (
        db.query(models.StageLog)
        .join(models.ProductionBatch)
        .filter(models.ProductionBatch.batch_code == batch_code)
        .all()
    )

def get_all_batches(db: Session):
    return db.query(models.ProductionBatch).all()


