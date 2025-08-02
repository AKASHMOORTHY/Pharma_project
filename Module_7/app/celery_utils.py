from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "dashboard_worker",
    broker = "redis://localhost:6379/0",
    # backend = None
    backend="redis://localhost:6379/0",
    include=[
        "app.tasks.report_tasks",
        "app.tasks.notifications",
    ]
)

celery_app.conf.timezone = 'Asia/Kolkata'
celery_app.conf.enable_utc = False

celery_app.conf.beat_schedule = {
    "generate-daily-qc-report": {
        "task": "app.tasks.report_tasks.generate_report",
        # "schedule": crontab(hour=21, minute=0),  # Every day at 9 PM
        "schedule": crontab(hour = 22, minute = 30),  # Every day at 3 30 PM
        "args": ("Daily QC Summary", "pdf", None, None)
    },
    "send-daily-alerts": {
        "task": "app.tasks.notifications.check_anomalies",
        "schedule": crontab(hour = 22, minute = 30),  # Daily at 8:30 AM
    },

    "cleanup-old-reports": {
    "task": "app.tasks.report_tasks.cleanup_old_reports",
    "schedule": crontab(hour = 22, minute = 30),  # every day at 3 AM
},
"weekly_qc_summary": {
        "task": "app.tasks.report_tasks.generate_configurable_report",
        "schedule": crontab(hour = 22, minute = 30, day_of_week="fri"),  # every Sunday at 8:30 AM
        #"schedule": crontab(hour=20, minute=0, day_of_week="sun"),  # every Sunday at 8 PM
        "args": [{
            "report_name": "Weekly QC Summary",
            "filters": {
                "start_date": "dynamic",  # we will replace this below
                "end_date": "dynamic"
            },
            "format": "PDF",
            "include_graphs": True,
            "scheduled": True
        }]
},
}

