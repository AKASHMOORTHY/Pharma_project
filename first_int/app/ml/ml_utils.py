import pandas as pd
import joblib
import os

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")  # Updated path

def predict_anomalies_from_excel(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path)

    if "Parameter" not in df.columns or "Observed Value" not in df.columns:
        raise ValueError("Excel must have 'Parameter' and 'Observed Value' columns.")

    predictions = []

    for _, row in df.iterrows():
        param = row["Parameter"]
        value = [[row["Observed Value"]]]

        model_path = os.path.join(MODEL_DIR, f"{param.replace(' ', '_')}.pkl")
        if not os.path.exists(model_path):
            print(f"⚠️ Model not found for {param}. Skipping...")
            predictions.append(0)
            continue

        try:
            model = joblib.load(model_path)
            prediction = model.predict(value)[0]
        except Exception as e:
            print(f"❌ Error loading model for {param}: {e}")
            prediction = 0

        predictions.append(prediction)

    df["prediction"] = predictions
    return df
