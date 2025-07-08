from sqlalchemy.orm import Session
from models.production_batch import ProductionBatch
from schemas.production_batch_schema import ProductionBatchCreate

def create_batch(db: Session, batch: ProductionBatchCreate):
    new_batch = ProductionBatch(**batch.dict())
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
   
    return new_batch

def list_batches(db: Session):
    return db.query(ProductionBatch).all()
