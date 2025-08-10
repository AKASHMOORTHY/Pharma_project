from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func

from app.database import SessionLocal
from app.models.qc_models import QCTest, QCTestResult, QCParameter
from app.models.anomaly_models import AnomalyRule, DetectedAnomaly
from app.crud.anomaly_crud import create_anomaly
from app.tasks.notification import send_email_alert  # ✅ import the Celery task
from app.tasks.celery_utils import celery_app
from app.ml.predict_from_db import predict_anomalies_from_db

# def check_out_of_range():
#     print("🔍 Running: check_out_of_range()")
#     
#     db = SessionLocal()
#     try:
#         rules = db.query(AnomalyRule).filter(
#             AnomalyRule.is_active == True,
#             AnomalyRule.source_table == "QCTestResult",
#             AnomalyRule.field_name == "observed_value",
#             AnomalyRule.condition == "outside_min_max"
#         ).all()
# 
#         results = db.query(QCTestResult).all()
# 
#         for result in results:
#             param = db.query(QCParameter).filter(QCParameter.id == result.parameter_id).first()
#             if not param:
#                 continue
# 
#             if result.observed_value < param.min_value or result.observed_value > param.max_value:
#                 for rule in rules:
#                     description = f"{param.name} value {result.observed_value} out of range ({param.min_value}–{param.max_value})"
#                     create_anomaly(
#                         db=db,
#                         rule_id=rule.id,
#                         source_id=str(result.test_id),
#                         severity=rule.severity,
#                         description=description
#                     )
#     except Exception as e:
#         print(f"❌ Error in check_out_of_range: {e}")
#         db.rollback()
#     finally:
#         db.close()
# 
#     print("✅ check_out_of_range completed.")


def check_missed_entries():
    print("🔍 Running: check_missed_entries()")
    
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        four_hours_ago = now - timedelta(hours=4)

        recent_qc = db.query(QCTest).filter(QCTest.date >= four_hours_ago).first()

        if not recent_qc:
            create_anomaly(
                db=db,
                rule_id=None,
                source_id="qc_shift_check",
                severity="medium",
                description="No QC test entry found in the last 4 hours."
            )
            
            # ✅ Send email alert asynchronously via Celery
            send_email_alert.delay(
                subject="🚨 QC Missed Entry Alert",
                message=f"No QC test entry was found between {four_hours_ago} and {now} UTC. Please investigate immediately.",
                # recipients=["truwwb@gmail.com"]
                
            )
    except Exception as e:
        print(f"❌ Error in check_missed_entries: {e}")
        db.rollback()
    finally:
        db.close()

    print("✅ check_missed_entries completed.")


def check_logical_sequence():
    print("🔍 Running: check_logical_sequence()")
    
    db = SessionLocal()
    try:
        # Sample logic: find QC tests marked as failed but used in production
        failed_qcs = db.query(QCTest).filter(QCTest.status == "FAILED").all()

        for test in failed_qcs:
            # ❗ Integrate with production usage check later
            description = f"Logical issue: Batch {test.source_id} marked as FAILED in QC but may have been used in production."
            
            create_anomaly(
                db=db,
                rule_id=None,
                source_id=test.source_id,
                severity="high",
                description=description
            )

            # 📧 Send email notification
            send_email_alert.delay(
                subject="🚨 Logical Anomaly Detected",
                message=description,
                # recipients=["truwwb@gmail.com"]  # 🔁 Replace with your real recipient

            )

            print(f"📧 Email alert sent for anomaly in batch {test.source_id}")
    except Exception as e:
        print(f"❌ Error in check_logical_sequence: {e}")
        db.rollback()
    finally:
        db.close()

    print("✅ check_logical_sequence completed.")


def check_repetitive_patterns():
    print("🔍 Running: check_repetitive_patterns()")
    
    db = SessionLocal()
    try:
        # Load active rule (optional fallback to None)
        rule = db.query(AnomalyRule).filter(
            AnomalyRule.name == "Repetitive Remarks",
            AnomalyRule.is_active == True
        ).first()

        repetitive = (
            db.query(QCTest.performed_by_id, QCTest.remarks, func.count())
            .group_by(QCTest.performed_by_id, QCTest.remarks)
            .having(func.count() > 3)
            .all()
        )

        for user_id, remark, count in repetitive:
            # Convert user_id to string for source_id, handling None, False, and other falsy values
            if user_id is None or user_id is False:
                user_id_str = "unknown"
            else:
                user_id_str = str(user_id)
            description = f"Repeated entries by user {user_id_str} with remark '{remark}' occurred {count} times."

            # ❗ Check for existing DetectedAnomaly
            existing = db.query(DetectedAnomaly).filter(
                DetectedAnomaly.source_id == user_id_str,
                DetectedAnomaly.description == description,
                DetectedAnomaly.status == "open"
            ).first()

            if existing:
                print(f"⚠️ Duplicate anomaly already exists for user {user_id_str} - Skipping.")
                continue

            # ✅ Create new DetectedAnomaly
            anomaly = DetectedAnomaly(
                test_id=None,  # You can try to get a related QC test ID if needed
                rule_id=rule.id if rule else None,
                source_id=user_id_str,
                severity=rule.severity if rule else "low",               
                description=description,
                status="open"
            )
            db.add(anomaly)
            db.commit()

            # 📧 Send email notification
            send_email_alert.delay(
                subject="🚨 Repetitive Pattern Detected",
                message=description,
                # recipients=["truwwb@gmail.com"]
            )

            print(f"📧 Email alert sent for repetitive pattern by user {user_id_str}")
    except Exception as e:
        print(f"❌ Error in check_repetitive_patterns: {e}")
        db.rollback()
    finally:
        db.close()

    print("✅ check_repetitive_patterns completed.")


def check_qc_drift():
    print("🔍 Running: check_qc_drift()")
    db = SessionLocal()
    try:
        parameters = db.query(QCParameter).all()

        for param in parameters:
            values = (
                db.query(QCTestResult.observed_value)
                .filter(QCTestResult.parameter_id == param.id)
                .order_by(QCTestResult.id)  # Optional: ensure chronological order
                .all()
            )
            values = [v[0] for v in values]

            if len(values) < 5:
                continue  # Not enough data for drift analysis

            avg = sum(values[:-1]) / len(values[:-1])
            latest = values[-1]

            if abs(latest - avg) > 0.5 * avg:
                description = (
                    f"Drift detected in '{param.name}': "
                    f"Latest value = {latest}, Historical average = {avg:.2f}"
                )

                create_anomaly(
                    db=db,
                    rule_id=None,
                    source_id="qc_drift",
                    severity="medium",
                    description=description
                )

                # 📧 Send email notification
                send_email_alert.delay(
                    subject="🚨 QC Drift Detected",
                    message=description,
                    # recipients=["truwwb@gmail.com"]
                )

                print("📧 Email alert sent for QC drift")
    except Exception as e:
        print(f"❌ Error in check_qc_drift: {e}")
        db.rollback()
    finally:
        db.close()

    print("✅ check_qc_drift completed.")


# def check_stock_mismatch():
#     print("🔍 Running: check_stock_mismatch()")

#     # TODO: Integrate with actual stock tables in the future
#     # Simulated mismatch detection (for demo)

#     simulated_stock = {"RM001": {"expected": 1000, "actual": 850}}

#     for stock_id, data in simulated_stock.items():
#         diff = abs(data["expected"] - data["actual"])
#         if diff > 100:
#             create_anomaly(
#                 db=db,
#                 rule_id=None,
#                 source_id=stock_id,
#                 severity="high",
#                 description=f"Stock mismatch for {stock_id}: Expected {data['expected']}, Actual {data['actual']}"
#             )

#     print("✅ check_stock_mismatch completed.")



@celery_app.task(name="app.tasks.anomaly_checks.run_hourly_anomaly_check")
def run_hourly_anomaly_check():
    print("🕒 Running hourly anomaly checks...")
    
    # Rule-based anomaly detection
    # check_out_of_range()
    check_missed_entries()
    check_logical_sequence()
    check_repetitive_patterns()
    check_qc_drift()
    # check_stock_mismatch()

    # ML-based detection asynchronously
    predict_anomalies_from_db()

    print("✅ All anomaly checks completed.")
