# Architecture and data flow

1. **Telemetry input:** built-in generator or CSV upload.
2. **Validation:** seven numeric feature fields are required; values are coerced to numeric, infinite values become missing, and unusable rows are removed.
3. **Supervised detection:** a Random Forest learns from the `label` field (0 normal, 1 threat). A stratified hold-out split is used when possible.
4. **Anomaly detection:** Isolation Forest learns typical feature distributions and provides a second anomaly signal.
5. **Decision presentation:** classifier label, threat probability, anomaly flag, and a simplified severity tier are returned. Severity is a demo heuristic, not an operational incident priority.
6. **API/dashboard:** Flask serves JSON endpoints and the browser dashboard. Events are held in memory for the current process; restarting the server resets the session stream.

## Feature dictionary

See the input data table in the README. Feature names are intentionally generic and synthetic. A real dataset adapter should document units, observation windows, data lineage, label quality, and missing-value policy.

## Safety boundary

Simulation is generated in-process. It does not create packets, scan hosts, send login attempts, or connect to external infrastructure.
