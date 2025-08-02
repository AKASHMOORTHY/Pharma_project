from app.celery_utils import celery_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env at module level like in report_tasks.py

print("env Loaded for notifications")
print("SMTP_USER:", os.getenv("SMTP_USER"))
print("EMAIL_TO:", os.getenv("EMAIL_TO"))

@celery_app.task
def check_anomalies():
    sender_email = os.getenv("SMTP_USER")
    sender_password = os.getenv("SMTP_PASSWORD")
    receiver_email = os.getenv("EMAIL_TO")

    subject = "Daily Anomaly Alert"
    body = "This is your daily anomaly alert. Please check the system for details."

    # Create the email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Alert email sent successfully.")

    except Exception as e:
        print(f"Failed to send alert email: {e}") 