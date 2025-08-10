from sqlalchemy.orm import Session
from app.models.anomaly_models import AnomalyRule, DetectedAnomaly
from app.schemas.anomaly_schemas import AnomalyRuleCreate
from datetime import datetime

def create_rule(db: Session, rule: AnomalyRuleCreate):
    db_rule = AnomalyRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def get_rules(db: Session):
    return db.query(AnomalyRule).filter(AnomalyRule.is_active == True).all()

def create_anomaly(db: Session, rule_id: int, source_id: str, severity: str, description: str):
    anomaly = DetectedAnomaly(
        rule_id=rule_id,
        source_id=source_id,
        severity=severity,
        description=description
    )
    db.add(anomaly)
    db.commit()
    db.refresh(anomaly)
    return anomaly


def resolve_anomaly(db: Session, anomaly_id: int, resolved_by: str, resolution_notes: str = None):
    anomaly = db.query(DetectedAnomaly).filter(DetectedAnomaly.id == anomaly_id).first()
    if anomaly:
        anomaly.status = "resolved"
        anomaly.resolved_by = resolved_by
        anomaly.resolved_at = datetime.utcnow()
        
        # ✅ Append resolution note to description field
        if resolution_notes:
            anomaly.description = f"{anomaly.description}\n\n📝 Resolution Notes: {resolution_notes}"

        db.commit()
        db.refresh(anomaly)
    return anomaly


def ignore_anomaly(db: Session, anomaly_id: int):
    anomaly = db.query(DetectedAnomaly).filter(DetectedAnomaly.id == anomaly_id).first()
    if anomaly:
        anomaly.status = 'ignored'
        db.commit()
        db.refresh(anomaly)
    return anomaly


def get_all_anomalies(db: Session):
    return db.query(DetectedAnomaly).order_by(DetectedAnomaly.detected_at.desc()).all()
