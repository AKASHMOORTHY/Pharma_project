from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from typing import List
from app.dependencies import role_required

router = APIRouter(prefix="/api/dashboard/qc", tags=["QC"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.QCOut], dependencies=[Depends(role_required(["Manager", "QA"]))])
def get_qc_dashboard(db: Session = Depends(get_db)):
    return db.query(models.QualityCheck).all()
