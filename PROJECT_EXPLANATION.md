# Project explanation (student presentation)

## In simple words

This project is like a smart monitoring assistant. It looks at simplified network activity measurements and estimates whether a record resembles normal activity or a suspicious pattern. It also checks whether a record looks unusual compared with the traffic patterns learned by an anomaly detector. The dashboard displays results and lets a student safely generate simulated events.

## Technical summary

The application generates or ingests tabular telemetry, validates numeric features, then passes records through a scikit-learn Random Forest classifier and an Isolation Forest model. The classifier is evaluated with accuracy, precision, recall, F1 score, and a confusion matrix on a held-out split. Flask exposes inference and management endpoints, while a browser-based frontend visualizes event counts, model metrics, and individual predictions.

## Why it matters

Security teams may analyze large amounts of endpoint, authentication, and network telemetry. Detection systems can prioritize events for analyst review, but predictions can produce false positives and false negatives. Real organizations combine telemetry, rules, models, threat intelligence, and human investigation. This project demonstrates a small educational slice of that workflow, not a full enterprise SOC.

## Limitations to mention in an interview

- Training and default simulation data are synthetic.
- The feature definitions are illustrative, not directly compatible with a public dataset without mapping.
- The demo has no packet capture, SIEM integration, authentication, or persistent event database.
- Model scores are not proof of an actual attack; real performance must be measured on representative unseen data.
