"""Training, evaluation, and prediction utilities."""
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from src.config import FEATURES, LABEL, MODEL_DIR, REPORT_DIR

MODEL_PATH = MODEL_DIR / "threat_detector.joblib"
ANOMALY_PATH = MODEL_DIR / "anomaly_detector.joblib"
REPORT_PATH = REPORT_DIR / "training_metrics.json"

def prepare_frame(df):
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError("CSV is missing required feature columns: " + ", ".join(missing))
    clean = df.copy()
    for col in FEATURES:
        clean[col] = pd.to_numeric(clean[col], errors="coerce")
    clean[FEATURES] = clean[FEATURES].replace([np.inf, -np.inf], np.nan)
    clean = clean.dropna(subset=FEATURES)
    if clean.empty:
        raise ValueError("No usable rows remain after numeric cleaning.")
    return clean

def train_models(df):
    clean = prepare_frame(df)
    if LABEL not in clean.columns:
        raise ValueError(f"Training data must include a '{LABEL}' column (0=normal, 1=threat).")
    y = pd.to_numeric(clean[LABEL], errors="coerce")
    valid = y.isin([0, 1])
    clean, y = clean.loc[valid], y.loc[valid].astype(int)
    if len(clean) < 20 or y.nunique() < 2:
        raise ValueError("Training requires at least 20 valid rows and both label classes (0 and 1).")
    X = clean[FEATURES]
    stratify = y if y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=stratify)
    classifier = Pipeline([("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(n_estimators=180, max_depth=14, class_weight="balanced", random_state=42, n_jobs=-1))])
    classifier.fit(X_train, y_train)
    pred = classifier.predict(X_test)
    metrics = {"rows": int(len(clean)), "train_rows": int(len(X_train)), "test_rows": int(len(X_test)),
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "precision": round(float(precision_score(y_test, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, pred, zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_test, pred, labels=[0,1]).tolist(),
        "classification_report": classification_report(y_test, pred, output_dict=True, zero_division=0)}
    anomaly = Pipeline([("imputer", SimpleImputer(strategy="median")),
        ("model", IsolationForest(n_estimators=160, contamination=0.12, random_state=42))])
    anomaly.fit(X_train)
    joblib.dump({"pipeline": classifier, "features": FEATURES}, MODEL_PATH)
    joblib.dump({"pipeline": anomaly, "features": FEATURES}, ANOMALY_PATH)
    REPORT_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics

def load_models():
    if not MODEL_PATH.exists() or not ANOMALY_PATH.exists():
        return None, None
    return joblib.load(MODEL_PATH)["pipeline"], joblib.load(ANOMALY_PATH)["pipeline"]

def predict_rows(df):
    clean = prepare_frame(df)
    clf, anomaly = load_models()
    if clf is None:
        raise RuntimeError("Models are not trained yet. Run the training step first.")
    X = clean[FEATURES]
    predictions = clf.predict(X).astype(int)
    probabilities = clf.predict_proba(X)[:, 1]
    anomaly_flags = (anomaly.predict(X) == -1).astype(int)
    results = clean.copy()
    results["threat_prediction"] = predictions
    results["threat_probability"] = np.round(probabilities, 4)
    results["anomaly_flag"] = anomaly_flags
    results["severity"] = ["HIGH" if p == 1 and prob >= .75 else "MEDIUM" if p == 1 or a == 1 else "LOW" for p, prob, a in zip(predictions, probabilities, anomaly_flags)]
    results["alert"] = ["Suspicious activity detected" if p or a else "No immediate signal" for p, a in zip(predictions, anomaly_flags)]
    return results
