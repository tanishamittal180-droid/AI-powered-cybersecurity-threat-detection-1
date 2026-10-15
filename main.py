"""Convenient CLI for the AI Cybersecurity Threat Detection demo."""
import argparse
import pandas as pd
from src.config import FEATURES
from src.data_generator import ensure_sample_dataset, generate_dataset
from src.ml_pipeline import train_models, predict_rows
from src.visualizations import save_confusion_matrix

def main():
    parser = argparse.ArgumentParser(description="AI-powered cybersecurity threat detection demo")
    parser.add_argument("command", choices=["train", "demo", "predict-sample", "generate-data"])
    parser.add_argument("--rows", type=int, default=100)
    parser.add_argument("--input", help="CSV path for training or prediction")
    args = parser.parse_args()
    if args.command == "generate-data":
        path = ensure_sample_dataset(); print(f"Sample dataset: {path}"); return
    if args.command == "train":
        path = args.input or str(ensure_sample_dataset())
        metrics = train_models(pd.read_csv(path)); save_confusion_matrix(metrics)
        print("Training complete")
        for key in ("rows", "accuracy", "precision", "recall", "f1"): print(f"{key}: {metrics[key]}")
        print("Model saved under models/ and metrics under outputs/reports/"); return
    if args.command == "demo":
        data = generate_dataset(args.rows)
        result = predict_rows(data[FEATURES])
        print(result[[*FEATURES,"threat_prediction","threat_probability","anomaly_flag","severity","alert"]].head(20).to_string(index=False))
        out = __import__('pathlib').Path("outputs/cli_demo_predictions.csv")
        result.to_csv(out,index=False); print(f"\nSaved {len(result)} predictions to {out}"); return
    if args.command == "predict-sample":
        path = args.input or str(ensure_sample_dataset())
        df = pd.read_csv(path)
        result = predict_rows(df[FEATURES])
        out = __import__('pathlib').Path("outputs/predictions.csv"); result.to_csv(out,index=False)
        print(f"Analyzed {len(result)} rows. Threat predictions: {(result.threat_prediction==1).sum()}. Saved: {out}")
if __name__ == "__main__": main()
