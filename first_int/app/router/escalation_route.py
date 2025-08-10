from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import escalation_crud 
from app.schemas import escalation_schemas  
from app.tasks.notification import check_escalations
from app.celery_worker import celery_app


router = APIRouter(
    prefix="/api/auth",
    tags=["Escalation"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/notifications/", response_model=list[escalation_schemas.Notification])
def get_notifications(user_id: int, db: Session = Depends(get_db)):
    return escalation_crud.get_user_notifications(db, user_id=user_id)

@router.post("/notifications/", response_model = escalation_schemas.Notification)
def create_notification(notification: escalation_schemas.NotificationCreate, db: Session = Depends(get_db)):
    return escalation_crud.create_notification(db, notification)

@router.post("/notifications/mark-seen/")
def mark_seen(user_id: int, db: Session = Depends(get_db)):
    escalation_crud.mark_notifications_seen(db, user_id)
    return {"message": "Notifications marked as seen"}

# -- Escalation Rules --

@router.get("/admin/escalation-rules/", response_model = list[escalation_schemas.EscalationRule])
def get_escalation_rules(db: Session = Depends(get_db)):
    return escalation_crud.get_all_escalation_rules(db)

@router.post("/admin/escalation-rules/", response_model = escalation_schemas.EscalationRule)
def create_escalation(rule: escalation_schemas.EscalationRuleCreate, db: Session = Depends(get_db)):
    return escalation_crud.create_escalation_rule(db, rule)

@router.post("/admin/run-escalation/")
def run_escalation_check(db: Session = Depends(get_db)):
    check_escalations(db)
    return {"message": "Escalation check completed"}


# @router.post("/send-sms/")
# def trigger_sms(req: escalation_schemas.SMSRequest):
#     celery_app.send_task("send_sms_task", args=[req.to_number, req.message])
#     return {"message": "SMS task queued"}