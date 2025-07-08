from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas.material_schema import MaterialBatch, MaterialBatchCreate
from ..services import material_service
from ..dependencies import get_db

router = APIRouter(
    prefix="/materials",
    tags=["Materials"]
)

@router.post("/", response_model=MaterialBatch)
def create_batch(batch: MaterialBatchCreate, db: Session = Depends(get_db)):
    return material_service.create_batch(db, batch)

@router.get("/", response_model=list[MaterialBatch])
def list_batches(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return material_service.get_batches(db, skip, limit)
