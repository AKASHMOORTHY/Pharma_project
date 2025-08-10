from sqlalchemy.orm import Session
from app.schemas import escalation_schemas
from app.models import escalation_models, user_models
from datetime import datetime

# ---------- Users ----------
def get_user(db: Session, user_id: int):
    return db.query(user_models.User).filter(user_models.User.id == user_id).first()

# ---------- Notifications ----------
def create_notification(db: Session, notif: escalation_schemas.NotificationCreate):
    db_notif = escalation_models.Notification(
        recipient_id = notif.recipient_id,
        message = notif.message,
        event_type = notif.event_type,
        related_object_id=notif.related_object_id,
        created_at=notif.created_at or datetime.utcnow()
    )
    db.add(db_notif)
    db.commit()
    db.refresh(db_notif)
    return db_notif

def get_user_notifications(db: Session, user_id: int):
    return db.query(escalation_models.Notification).filter(escalation_models.Notification.recipient_id == user_id).all()

def mark_notifications_seen(db: Session, user_id: int):
    db.query(escalation_models.Notification).filter(
        escalation_models.Notification.recipient_id == user_id,
        escalation_models.Notification.seen == False
    ).update({escalation_models.Notification.seen: True})
    db.commit()

# ---------- Escalation Rules ----------
def create_escalation_rule(db: Session, rule: escalation_schemas.EscalationRuleCreate):
    db_rule = escalation_models.EscalationRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)

    return db_rule

def get_all_escalation_rules(db: Session):
    return db.query(escalation_models.EscalationRule).all()
