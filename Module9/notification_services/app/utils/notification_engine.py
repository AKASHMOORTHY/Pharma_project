from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from notification_services.app import models, crud, schemas
import aiosmtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from twilio.rest import Client

import os

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
from notification_services.app.celery_worker import celery_app

@celery_app.task(name="notification_services.app.routes.notification.run_escalation_task")
def run_escalation_task():
    from notification_services.app.database import SessionLocal

    print("Automatic escalation task triggered.")

    db = SessionLocal()
    try:
        check_escalations(db)
    except Exception as e:
        print(f"Error in escalation task: {e}")

    finally:
        db.close()


def check_escalations(db: Session):
    print("Running escalation task...")
    rules = db.query(models.EscalationRule).filter(models.EscalationRule.active == True).all()

    for rule in rules:
        overdue_notifications = db.query(models.Notification).filter(
            models.Notification.event_type == rule.event_type,
            models.Notification.seen == False,
            models.Notification.created_at < datetime.utcnow() - timedelta(minutes=rule.trigger_after_minutes)
        ).all()
        print(f"Overdue notifications: {len(overdue_notifications)}")


        for evt in overdue_notifications:
            escalated_msg = f"Escalated: {evt.message}"
            print(f"Escalating notification {evt.id} to user {rule.escalate_to_id}...")

            # Create new escalated notification
            new_notif = schemas.NotificationCreate(
                recipient_id=rule.escalate_to_id,
                event_type=f"{evt.event_type} (Escalated)",
                message=escalated_msg,
                related_object_id=evt.related_object_id
            )
            crud.create_notification(db, new_notif)

            # Fetch recipient details (email and phone)
            recipient = db.query(models.User).filter(models.User.id == rule.escalate_to_id).first()
            if recipient:
                # Send Email
                if recipient.email:
                    print('email started')
                    subject = "Escalated Notification Alert"
                    content = f"Dear {recipient.full_name},\n\nYou have a new escalated notification:\n\n{escalated_msg}"
                    try:
                        import asyncio
                        asyncio.run(send_email(recipient.email, subject, content))
                    except Exception as e:
                        print(f"Failed to send email: {e}")
                print('email ended')


                # Send SMS
                if recipient.phone:
                    print('sms started')
                    content_msg = f"Dear {recipient.full_name},\n\nYou have a new escalated notification:\n\n{escalated_msg}"


                    try:
                        import asyncio
                        print('sms started')
                        asyncio.run(send_sms_task(recipient.phone, content_msg))
                    except Exception as e:
                        print(f"Failed to send SMS: {e}")
                    
                    print('sms ended')
    print("outside check_escalations")



async def send_email(to_email: str, subject: str, content: str):
    message = EmailMessage()
    message["From"] = EMAIL_USERNAME
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(content)

    await aiosmtplib.send(
        message,
        hostname=EMAIL_HOST,
        port=EMAIL_PORT,
        start_tls=True,
        username=EMAIL_USERNAME,
        password=EMAIL_PASSWORD,
    )





async def send_sms_task(to_number: str, message: str):


    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

    client = Client(account_sid, auth_token)

    response = client.messages.create(
        body=message,
        from_=twilio_number,
        to=to_number
    )

    print(f"✅ SMS sent to {to_number}, SID: {response.sid}")
