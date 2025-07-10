# app/routers/production_batch.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app import schemas, crud
from app.schemas import ProductionBatchCreate
from app.dependencies import get_db  # ✅ good

router = APIRouter()

@router.post("/")
def create_batch(batch: ProductionBatchCreate, db: Session = Depends(get_db)):
    return crud.create_batch(db, batch)

@router.get("/", response_model=List[schemas.ProductionBatchResponse])
def get_batches(db: Session = Depends(get_db)):
    return crud.get_all_batches(db)
