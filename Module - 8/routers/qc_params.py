from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import QCParameter
from schemas import QCParameterCreate, QCParameterOut
from typing import List

router = APIRouter()

@router.get("/", response_model=List[QCParameterOut])
def get_qc_params(db: Session = Depends(get_db)):
    return db.query(QCParameter).all()

@router.post("/", response_model=QCParameterOut)
def create_qc_param(param: QCParameterCreate, db: Session = Depends(get_db)):
    db_param = QCParameter(**param.dict())
    db.add(db_param)
    db.commit()
    db.refresh(db_param)
    return db_param
