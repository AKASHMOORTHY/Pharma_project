from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.anomaly_schemas import AnomalyRuleCreate, AnomalyRuleOut,DetectedAnomalyOut, AnomalyResolveInput

from app.crud import anomaly_crud

router = APIRouter(prefix="/api/anomalies", tags=["Anomalies"])


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---- RULES ENDPOINTS ----

@router.post("/rules/", response_model=AnomalyRuleOut)
def create_rule(rule: AnomalyRuleCreate, db: Session = Depends(get_db)):
    return anomaly_crud.create_rule(db, rule)


@router.get("/rules/", response_model=list[AnomalyRuleOut])
def list_rules(db: Session = Depends(get_db)):
    return anomaly_crud.get_rules(db)


# ---- ANOMALIES ENDPOINTS ----

@router.get("/", response_model=list[DetectedAnomalyOut])
def fetch_all_anomalies(db: Session = Depends(get_db)):
    return anomaly_crud.get_all_anomalies(db)


@router.post("/{anomaly_id}/resolve/")
def resolve_anomaly(
    anomaly_id: int,
    payload: AnomalyResolveInput,
    db: Session = Depends(get_db)
):
    anomaly = anomaly_crud.resolve_anomaly(
        db=db,
        anomaly_id=anomaly_id,
        resolved_by=payload.resolved_by,
        resolution_notes=payload.resolution_notes
    )
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return {"status": "resolved", "anomaly_id": anomaly_id}


@router.post("/{anomaly_id}/ignore/")
def ignore_anomaly(anomaly_id: int, db: Session = Depends(get_db)):
    anomaly = anomaly_crud.ignore_anomaly(db, anomaly_id)
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return {"status": "ignored", "anomaly_id": anomaly_id}
