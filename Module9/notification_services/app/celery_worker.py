from celery import Celery
from dotenv import load_dotenv
from celery.schedules import crontab
import os

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "notification_worker",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.timezone = 'Asia/Kolkata'

celery_app.conf.beat_schedule = {
    "run-escalation-task-every-5-minutes": {
        "task": "notification_services.app.routes.notification.run_escalation_task",
        "schedule": crontab(minute="*/1"),
    }
}

# IMPORT THE MODULE THAT DEFINES THE TASK
from notification_services.app.utils import notification_engine  # This registers the task
