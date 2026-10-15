"""Create safe, synthetic network telemetry for local learning and demos."""
import numpy as np
import pandas as pd
from src.config import FEATURES, LABEL, SAMPLE_DIR

def generate_dataset(n_rows=2400, seed=42):
    rng = np.random.default_rng(seed)
    labels = rng.choice([0, 1], size=n_rows, p=[0.78, 0.22])
    normal = labels == 0
    packet_size = np.where(normal, rng.normal(720, 260, n_rows), rng.normal(1320, 390, n_rows))
    failed_logins = np.where(normal, rng.poisson(0.35, n_rows), rng.poisson(5.5, n_rows))
    request_frequency = np.where(normal, rng.gamma(2.0, 9.0, n_rows), rng.gamma(5.0, 34.0, n_rows))
    connection_duration = np.where(normal, rng.gamma(2.5, 4.0, n_rows), rng.gamma(1.4, 1.6, n_rows))
    bytes_out = np.where(normal, rng.gamma(2.2, 850, n_rows), rng.gamma(4.2, 2400, n_rows))
    unique_ports = np.where(normal, rng.poisson(1.4, n_rows), rng.poisson(8.0, n_rows))
    protocol_encoded = rng.choice([0, 1, 2], size=n_rows, p=[0.68, 0.22, 0.10])
    df = pd.DataFrame({"packet_size": packet_size, "failed_logins": failed_logins,
        "request_frequency": request_frequency, "connection_duration": connection_duration,
        "bytes_out": bytes_out, "unique_ports": unique_ports, "protocol_encoded": protocol_encoded,
        LABEL: labels})
    for col in FEATURES:
        df[col] = df[col].clip(lower=0).round(3)
    return df

def ensure_sample_dataset():
    path = SAMPLE_DIR / "synthetic_network_traffic.csv"
    if not path.exists():
        generate_dataset().to_csv(path, index=False)
    return path

if __name__ == "__main__":
    path = ensure_sample_dataset()
    print(f"Synthetic demo dataset saved: {path}")
