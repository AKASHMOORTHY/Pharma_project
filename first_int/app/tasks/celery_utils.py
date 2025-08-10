from celery import Celery
from celery.schedules import crontab


celery_app = Celery(
    "dashboard_worker",
    broker = "redis://localhost:6379/0",
    # backend = None
    backend="redis://localhost:6379/0",
    include=[
        "app.tasks.report_tasks",
        "app.tasks.notification",
        "app.tasks.anomaly_checks", 
        "app.tasks.locking",        
    ]
)

celery_app.conf.timezone = 'Asia/Kolkata'
celery_app.conf.enable_utc = False

# Windows-specific configuration
celery_app.conf.update(
    worker_pool='solo',  # Use single-threaded pool for Windows
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    result_expires=3600,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=False,
)

# Update the beat schedule to include all scheduled tasks
celery_app.conf.beat_schedule = {
    "hourly-anomaly-scan": {
        "task": "app.tasks.anomaly_checks.run_hourly_anomaly_check",
        "schedule": crontab(hour = 16, minute = 45),  # every 10 seconds for testing
    },
    "lock-every-10-seconds": {
        "task": "app.tasks.locking.lock_shift_data",
        "schedule": crontab(hour = 16, minute = 45),  # ⏱️ every 10 seconds
    },
    "generate-daily-qc-report": {
        "task": "app.tasks.report_tasks.generate_report",
        # "schedule": crontab(hour=21, minute=0),  # Every day at 9 PM
        "schedule": crontab(hour = 16, minute = 45),  # Every day at 9:16 AM
       "args": ("Daily QC Summary", "pdf", None, None)
    },
    "send-daily-alerts": {
        "task": "app.tasks.report_tasks.generate_anomaly_report",
        "schedule": crontab(hour = 16, minute = 45),  # Daily at 21:30 AM
    },
    "cleanup-old-reports": {
        "task": "app.tasks.report_tasks.cleanup_old_reports",
        "schedule": crontab(hour = 16, minute = 45),  # every day at 3 AM
    },
    "weekly_qc_summary": {
        "task": "app.tasks.report_tasks.generate_configurable_report",
        "schedule": crontab(hour = 16, minute = 45, day_of_week="Sun"),  # every Saturday at 9:16 AM
        # "schedule": crontab(hour=45, minute=0, day_of_week="sun"),  # every Sunday at 21 PM
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
    "run-escalation-task-every-5-minutes": {
        "task": "app.tasks.notification.run_escalation_task",
        "schedule": crontab(hour = 16, minute = 45)
    }
}


