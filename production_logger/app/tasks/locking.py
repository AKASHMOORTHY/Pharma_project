from celery import Celery
from celery.schedules import crontab
from datetime import datetime, time
from app.database import SessionLocal
from app.models import StageLog

celery = Celery("myapp", broker="redis://localhost:6380/0", backend="redis://localhost:6380/0")

# 🔁 Run every 10 seconds (for testing)
celery.conf.beat_schedule = {
    'lock-every-10-seconds': {
        'task': 'app.tasks.locking.lock_shift_data',
        'schedule': 10.0,  # ⏱️ every 10 seconds
    }
}

@celery.task
def lock_shift_data():
    db = SessionLocal()
    try:
        now = datetime.now()
        print(f"🔁 Checking at {now.strftime('%H:%M:%S')}")
        
        unlocked_logs = db.query(StageLog).filter(StageLog.is_locked == 0).all()
        
        if unlocked_logs:
            for log in unlocked_logs:
                log.is_locked = 1
            db.commit()
            print(f"✅ Locked {len(unlocked_logs)} stage logs.")
        else:
            print("🚫 No unlocked logs found.")
    except Exception as e:
        print("❌ Error during locking:", str(e))
        db.rollback()
    finally:
        db.close()

