from datetime import datetime
from app.database import SessionLocal
from app.models.production_models import StageLog
from app.tasks.celery_utils import celery_app
from sqlalchemy.orm import Session
from app.models.qc_models import QCTestResult


@celery_app.task
def lock_shift_data():
    db = SessionLocal()
    try:
        now = datetime.now()
        print(f"🔁 Checking at {now.strftime('%H:%M:%S')}")
        
        unlocked_logs = db.query(StageLog).filter(StageLog.is_locked == False).all()
        
        if unlocked_logs:
            for log in unlocked_logs:
                log.is_locked = True
            db.commit()
            print(f"✅ Locked {len(unlocked_logs)} stage logs.")
        else:
            print("🚫 No unlocked logs found.")
    except Exception as e:
        print("❌ Error during locking:", str(e))
        db.rollback()
    finally:
        db.close()

# app/tasks/scheduler.py

# @celery_app.task
# def scan_database_for_anomalies():
#     db: Session = SessionLocal()
#     print("🔍 Running hourly anomaly scan...")

#     all_results = db.query(QCTestResult).all()

#     # Rebuild inputs for rule engine
#     test_inputs = []
#     for result in all_results:
#         param = result.parameter.name if result.parameter else "Unknown"
#         test_inputs.append({
#             "source_id": f"QC{result.test_id:03d}",
#             "parameter": param,
#             "observed_value": result.observed_value
#         })

#     # Run detection
#     # detect_anomalies_from_qc(db, test_inputs)

#     print(f"✅ Hourly scan complete. {len(test_inputs)} records checked.")

