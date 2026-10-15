from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
SAMPLE_DIR = DATA_DIR / "sample"
MODEL_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"
REPORT_DIR = OUTPUT_DIR / "reports"
FIGURE_DIR = OUTPUT_DIR / "figures"
for directory in (SAMPLE_DIR, MODEL_DIR, OUTPUT_DIR, REPORT_DIR, FIGURE_DIR):
    directory.mkdir(parents=True, exist_ok=True)
FEATURES = ["packet_size", "failed_logins", "request_frequency", "connection_duration", "bytes_out", "unique_ports", "protocol_encoded"]
LABEL = "label"
