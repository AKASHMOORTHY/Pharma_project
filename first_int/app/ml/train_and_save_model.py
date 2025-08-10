import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

# ✅ Load the dataset
script_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(script_dir, "ML test.xlsx")
df = pd.read_excel(excel_path)

# ✅ Normalize column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
print("✅ Normalized Columns:", df.columns.tolist())

# ✅ Check required columns
required_cols = ["parameter", "observed_value", "result"]
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"❌ Missing required column: {col}")

# ✅ Create binary label: 'fail' = 1, 'pass' = 0
df["label"] = df["result"].apply(lambda x: 1 if str(x).strip().lower() == "fail" else 0)

# ✅ Define model mapping for each test
model_mapping = {
    "ph": RandomForestClassifier(),
    "moisture": RandomForestClassifier(),
    "starch": DecisionTreeClassifier(),
    "appearance": GaussianNB(),
    "bulk_density": KNeighborsClassifier(),
    "angle_of_repose": LogisticRegression(max_iter=1000),
    "others": SVC(probability=True)
}

# ✅ Prepare model directory
model_dir = os.path.abspath(os.path.join("app", "ml", "models"))
os.makedirs(model_dir, exist_ok=True)
print(f"📂 Models will be saved to: {model_dir}")

trained_count = 0

# ✅ Train models per parameter
for param, group in df.groupby("parameter"):
    sanitized_param = param.strip().lower().replace(" ", "_").replace("%", "")
    
    if group.shape[0] < 10:
        print(f"⚠️ Skipping {param} - Not enough data ({len(group)} rows)")
        continue

    # Feature and label
    X = group[["observed_value"]]
    y = group["label"]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Get model
    model = model_mapping.get(sanitized_param, model_mapping["others"])

    # Train
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Save model
    model_path = os.path.join(model_dir, f"{sanitized_param}.pkl")
    joblib.dump(model, model_path)

    if os.path.exists(model_path):
        print(f"✅ {param}: Model saved at {model_path} | Accuracy: {accuracy:.2f}")
    else:
        print(f"❌ {param}: Model NOT saved!")

    trained_count += 1

print(f"\n🎯 Total models trained and saved: {trained_count}")
