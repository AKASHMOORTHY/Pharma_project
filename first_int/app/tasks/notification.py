# app/tasks/notifications.py

from app.tasks.celery_utils import celery_app
from email.message import EmailMessage
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import escalation_models,user_models
from app.schemas import escalation_schemas 
from app.crud import escalation_crud
from dotenv import load_dotenv
import aiosmtplib
from twilio.rest import Client
import smtplib
import os

load_dotenv()

print("env Loaded for notifications")
print("SMTP_USER:", os.getenv("SMTP_USER"))
print("EMAIL_TO:", os.getenv("EMAIL_TO"))

    
@celery_app.task(name="app.tasks.notification.send_email_alert")
def send_email_alert(subject: str, message: str):
    EMAIL_SENDER = os.getenv("SMTP_USER")
    EMAIL_PASSWORD = os.getenv("SMTP_PASSWORD")
    EMAIL_DEFAULT_RECEIVER = os.getenv("EMAIL_TO")

    msg = EmailMessage()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_DEFAULT_RECEIVER
    msg["Subject"] = subject
    msg.set_content(message)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(" Email sent successfully!")
        return {"status": "Email sent"}
    except Exception as e:
        print(f" Failed to send email: {e}")
        return {"status": "Failed", "error": str(e)}

# Module_9

EMAIL_HOST = os.getenv("SMTP_HOST")
EMAIL_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_USERNAME = os.getenv("SMTP_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


@celery_app.task(name="app.tasks.notification.run_escalation_task")
def run_escalation_task():
    from app.database import SessionLocal

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
    rules = db.query(escalation_models.EscalationRule).filter(escalation_models.EscalationRule.active == True).all()

    for rule in rules:
        overdue_notifications = db.query(escalation_models.Notification).filter(
            escalation_models.Notification.event_type == rule.event_type,
            escalation_models.Notification.seen == False,
            escalation_models.Notification.created_at < datetime.utcnow() - timedelta(minutes=rule.trigger_after_minutes)
        ).all()
        print(f"Overdue notifications: {len(overdue_notifications)}")


        for evt in overdue_notifications:
            escalated_msg = f"Escalated: {evt.message}"
            print(f"Escalating notification {evt.id} to user {rule.escalate_to_id}...")

            # Create new escalated notification
            new_notif = escalation_schemas.NotificationCreate(
                recipient_id=rule.escalate_to_id,
                event_type=f"{evt.event_type} (Escalated)",
                message=escalated_msg,
                related_object_id=evt.related_object_id
            )
            escalation_crud.create_notification(db, new_notif)

            # Fetch recipient details (email and phone)
            recipient = db.query(user_models.User).filter(user_models.User.id == rule.escalate_to_id).first()
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


            """  # Send SMS
                if recipient.phone:
                    print('sms started')
                    content_msg = f"Dear {recipient.full_name},\n\nYou have a new escalated notification:\n\n{escalated_msg}"


                    try:
                        import asyncio
                        print('sms started')
                        asyncio.run(send_sms_task(recipient.phone, content_msg))
                    except Exception as e:
                        print(f"Failed to send SMS: {e}")
                    
                    print('sms ended') """
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
