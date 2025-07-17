from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import SystemPreference
from schemas import SystemPreferenceCreate, SystemPreferenceOut
from typing import List

router = APIRouter()

@router.get("/", response_model=List[SystemPreferenceOut])
def get_preferences(db: Session = Depends(get_db)):
    return db.query(SystemPreference).all()

@router.post("/", response_model=SystemPreferenceOut)
def create_preference(pref: SystemPreferenceCreate, db: Session = Depends(get_db)):
    db_pref = SystemPreference(**pref.dict())
    db.add(db_pref)
    db.commit()
    db.refresh(db_pref)
    return db_pref
