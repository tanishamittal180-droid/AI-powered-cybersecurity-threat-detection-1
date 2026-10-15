from datetime import datetime, timezone
import io
import json
import pandas as pd
from flask import Flask, jsonify, render_template, request
from src.config import FEATURES, LABEL, OUTPUT_DIR, REPORT_DIR

from src.data_generator import generate_dataset, ensure_sample_dataset
from src.ml_pipeline import train_models, predict_rows, load_models, REPORT_PATH
from src.visualizations import save_confusion_matrix

app = Flask(__name__)
EVENTS = []
DATASET_PATH = ensure_sample_dataset()

def bootstrap():
    clf, _ = load_models()
    if clf is None:
        metrics = train_models(pd.read_csv(DATASET_PATH))
        save_confusion_matrix(metrics)

bootstrap()

def seed_events():
    if EVENTS:
        return
    demo = generate_dataset(35, seed=101)
    result = predict_rows(demo[FEATURES])
    for i, row in result.iterrows():
        EVENTS.append({"id": i+1, "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "event_type": "Simulated network event", "prediction": "THREAT" if row.threat_prediction else "NORMAL",
            "severity": row.severity, "probability": float(row.threat_probability),
            "alert": row.alert, "features": {k: float(row[k]) for k in FEATURES}})
seed_events()

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/health")
def health():
    return jsonify({"status":"ok", "model_loaded": load_models()[0] is not None, "mode":"synthetic/local demo"})

@app.get("/api/summary")
def summary():
    threats = sum(e["prediction"] == "THREAT" for e in EVENTS)
    high = sum(e["severity"] == "HIGH" for e in EVENTS)
    return jsonify({"total_events":len(EVENTS), "threats":threats, "normal":len(EVENTS)-threats,
        "high_severity":high, "threat_rate":round(threats/max(1,len(EVENTS))*100,1),
        "metrics": json.loads(REPORT_PATH.read_text()) if REPORT_PATH.exists() else {},
        "updated_at":datetime.now(timezone.utc).isoformat(timespec="seconds")})

@app.get("/api/events")
def events():
    limit = min(max(request.args.get("limit", 100, type=int), 1), 500)
    return jsonify(list(reversed(EVENTS[-limit:])))

@app.post("/api/simulate")
def simulate():
    body = request.get_json(silent=True) or {}
    count = min(max(int(body.get("count", 10)), 1), 100)
    batch = generate_dataset(count, seed=int(datetime.now().timestamp()) % 100000)
    predicted = predict_rows(batch[FEATURES])
    created=[]
    start_id = max([e["id"] for e in EVENTS], default=0)+1
    for offset, (_, row) in enumerate(predicted.iterrows()):
        event = {"id":start_id+offset, "timestamp":datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "event_type":"Simulated network event", "prediction":"THREAT" if row.threat_prediction else "NORMAL",
            "severity":row.severity, "probability":float(row.threat_probability), "alert":row.alert,
            "features":{k:float(row[k]) for k in FEATURES}}
        EVENTS.append(event); created.append(event)
    del EVENTS[:-500]
    return jsonify({"created":len(created), "events":created, "summary":{"threats":sum(x["prediction"]=="THREAT" for x in created)}})

@app.post("/api/predict")
def predict():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error":"Send a JSON object containing the seven numeric feature fields."}), 400
    try:
        frame = pd.DataFrame([{k:body.get(k) for k in FEATURES}])
        result = predict_rows(frame).iloc[0]
        return jsonify({"prediction":"THREAT" if result.threat_prediction else "NORMAL",
            "threat_probability":float(result.threat_probability), "anomaly_flag":int(result.anomaly_flag),
            "severity":result.severity, "alert":result.alert})
    except (ValueError, RuntimeError, TypeError) as exc:
        return jsonify({"error":str(exc)}), 400

@app.post("/api/upload")
def upload():
    file = request.files.get("file")
    if not file or not file.filename.lower().endswith(".csv"):
        return jsonify({"error":"Choose a CSV file."}), 400
    try:
        frame = pd.read_csv(io.BytesIO(file.read()))
        if LABEL in frame.columns:
            metrics = train_models(frame)
            save_confusion_matrix(metrics)
            return jsonify({"message":"Model retrained using uploaded labeled CSV.", "metrics":metrics})
        result = predict_rows(frame)
        out = OUTPUT_DIR / "latest_predictions.csv"
        result.to_csv(out, index=False)
        return jsonify({"message":"CSV analyzed. A prediction file was saved to outputs/latest_predictions.csv.",
            "rows":len(result), "threats":int((result.threat_prediction==1).sum()), "output_file":"outputs/latest_predictions.csv"})
    except Exception as exc:
        return jsonify({"error":str(exc)}), 400

@app.get("/api/metrics")
def metrics():
    return jsonify(json.loads(REPORT_PATH.read_text()) if REPORT_PATH.exists() else {})

if __name__ == "__main__":
    # Local demo only. Do not expose the development server to the public internet.
    app.run(host="127.0.0.1", port=5000, debug=False)
