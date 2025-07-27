from sqlalchemy.orm import Session
from notification_services.app import models, schemas
from datetime import datetime

# ---------- Users ----------
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# ---------- Notifications ----------
def create_notification(db: Session, notif: schemas.NotificationCreate):
    db_notif = models.Notification(
        recipient_id=notif.recipient_id,
        message=notif.message,
        event_type=notif.event_type,
        related_object_id=notif.related_object_id,
        created_at=notif.created_at or datetime.utcnow()
    )
    db.add(db_notif)
    db.commit()
    db.refresh(db_notif)
    return db_notif

def get_user_notifications(db: Session, user_id: int):
    return db.query(models.Notification).filter(models.Notification.recipient_id == user_id).all()

def mark_notifications_seen(db: Session, user_id: int):
    db.query(models.Notification).filter(
        models.Notification.recipient_id == user_id,
        models.Notification.seen == False
    ).update({models.Notification.seen: True})
    db.commit()

# ---------- Escalation Rules ----------
def create_escalation_rule(db: Session, rule: schemas.EscalationRuleCreate):
    db_rule = models.EscalationRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)

    return db_rule

def get_all_escalation_rules(db: Session):
    return db.query(models.EscalationRule).all()
