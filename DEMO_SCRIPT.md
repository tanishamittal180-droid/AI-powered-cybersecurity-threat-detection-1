# 90-second portfolio demo script

1. Start the app and open `http://127.0.0.1:5000`.
2. Explain that this is a local SOC-style dashboard backed by synthetic network telemetry.
3. Point out event totals, threat rate, and the held-out model metrics.
4. Set the simulator to 15 events and run it. Explain that every row is scored by both a classifier and an anomaly detector.
5. Filter the event stream to threats and export the event CSV.
6. Change failed logins and request frequency in the single-event form; submit and explain the probability is a model score, not certainty.
7. Close with the project limitations: synthetic data, no live packet capture, and need for real-world validation.
