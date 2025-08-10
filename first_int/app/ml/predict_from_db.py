# app/tasks/ml_predictor.py

import os
import joblib
import pandas as pd
from datetime import datetime

from app.database import SessionLocal
from app.models.qc_models import QCTestResult, QCParameter
from app.models.anomaly_models import DetectedAnomaly
from app.crud.anomaly_crud import create_anomaly
from app.tasks.notification import send_email_alert
from app.tasks.celery_utils import celery_app


MODEL_MAP = {
    "Moisture": "moisture.pkl",
    "pH": "ph.pkl",
    "Appearance": "appearance.pkl",
    "Starch": "starch.pkl",
    "Bulk Density": "bulk_density.pkl",
    "Angle of Repose": "angle_of_repose.pkl",  # ➕ Add this
}


@celery_app.task(name="app.tasks.ml_predictor.predict_anomalies_from_db")
def predict_anomalies_from_db():
    db = SessionLocal()
    try:
        results = (
            db.query(QCTestResult, QCParameter)
            .join(QCParameter, QCTestResult.parameter_id == QCParameter.id)
            .filter(QCTestResult.is_within_spec == False)  # 0 = not yet flagged as anomaly
            .filter(
                ~db.query(DetectedAnomaly)
                .filter(DetectedAnomaly.test_id == QCTestResult.id)
                .exists()
            )
            .all()
        )

        if not results:
            print("✅ No suspected test results found.")
            return

        print(f"🔍 Total suspected test results: {len(results)}")

        for result_obj, param_obj in results:
            test_name = param_obj.name
            observed_value = result_obj.observed_value
            print(f"🔎 Processing: {test_name} | Observed: {observed_value}")

            model_file = MODEL_MAP.get(test_name)
            if not model_file:
                print(f"⚠️ No model found for {test_name}. Skipping.")
                continue

            model_path = os.path.join("app", "ml", "models", model_file)
            if not os.path.exists(model_path):
                print(f"⚠️ Model file not found: {model_path}. Skipping.")
                continue

            try:
                model = joblib.load(model_path)

                # Get feature name (assume single feature model)
                feature_name = (
                    model.feature_names_in_[0] if hasattr(model, "feature_names_in_") else "value"
                )
                input_df = pd.DataFrame([{feature_name: observed_value}])

                prediction = model.predict(input_df)[0]

                if prediction == 0:
                    print(f"🚨 ML Anomaly Detected for {test_name} | Value: {observed_value}")
                    result_obj.is_within_spec = 1  # 1 = anomaly
                    db.commit()

                    anomaly = DetectedAnomaly(
                        test_id=result_obj.id,
                        source_id="ml_model",
                        severity="high",
                        status="open",
                        description=f"Anomaly detected by ML for {test_name}: {observed_value}"
                    )
                    db.add(anomaly)
                    db.commit()

                    send_email_alert.delay(
                        subject="🚨 QC Anomaly Detected by ML",
                        message=f"Parameter: {test_name}\nObserved: {observed_value}"
                    )
                else:
                    print(f"✅ Normal by ML: {test_name} | Value: {observed_value}")
                    result_obj.is_within_spec = 0  # mark as normal
                    db.commit()

            except Exception as e:
                print(f"❌ ML Prediction Error for {test_name}: {str(e)}")
                db.rollback()

    finally:
        db.close()
