from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from notification_services.app import crud, schemas, database
from notification_services.app.auth import get_db
from notification_services.app.utils.notification_engine import check_escalations
from notification_services.app.celery_worker import celery_app


router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"]
)




@router.get("/notifications/", response_model=list[schemas.Notification])
def get_notifications(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_notifications(db, user_id=user_id)

@router.post("/notifications/", response_model=schemas.Notification)
def create_notification(notification: schemas.NotificationCreate, db: Session = Depends(get_db)):
    return crud.create_notification(db, notification)

@router.post("/notifications/mark-seen/")
def mark_seen(user_id: int, db: Session = Depends(get_db)):
    crud.mark_notifications_seen(db, user_id)
    return {"message": "Notifications marked as seen"}

# -- Escalation Rules --

@router.get("/admin/escalation-rules/", response_model=list[schemas.EscalationRule])
def get_escalation_rules(db: Session = Depends(get_db)):
    return crud.get_all_escalation_rules(db)

@router.post("/admin/escalation-rules/", response_model=schemas.EscalationRule)
def create_escalation(rule: schemas.EscalationRuleCreate, db: Session = Depends(get_db)):
    return crud.create_escalation_rule(db, rule)



@router.post("/admin/run-escalation/")
def run_escalation_check(db: Session = Depends(get_db)):
    check_escalations(db)
    return {"message": "Escalation check completed"}


# @router.post("/send-sms/")
# def trigger_sms(req: schemas.SMSRequest):
#     celery_app.send_task("send_sms_task", args=[req.to_number, req.message])
#     return {"message": "SMS task queued"}