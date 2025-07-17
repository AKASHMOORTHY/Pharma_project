from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import AnomalyRule
from schemas import AnomalyRuleCreate, AnomalyRuleOut
from typing import List

router = APIRouter()

@router.get("/", response_model=List[AnomalyRuleOut])
def get_rules(db: Session = Depends(get_db)):
    return db.query(AnomalyRule).all()

@router.post("/", response_model=AnomalyRuleOut)
def create_rule(rule: AnomalyRuleCreate, db: Session = Depends(get_db)):
    db_rule = AnomalyRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule
