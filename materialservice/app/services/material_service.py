from sqlalchemy.orm import Session
from ..models.material_batch import MaterialBatch
from ..schemas.material_schema import MaterialBatchCreate

def create_batch(db: Session, batch: MaterialBatchCreate):
    db_batch = MaterialBatch(**batch.dict())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch

def get_batches(db: Session, skip: int = 0, limit: int = 10):
    return db.query(MaterialBatch).offset(skip).limit(limit).all()
