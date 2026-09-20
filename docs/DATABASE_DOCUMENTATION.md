# Database Schema & Storage Designs

TwinQ-Map utilizes **MongoDB** for flexible, scalable tracking of calibrations time-series data, model metrics, execution details, and authentication parameters.

## Collection Overview

### 1. Users
Stores user authentication details and role scopes:
- **Indexes**: Unique index on `username`, Unique index on `email`.
- **Validation**: BSON validation schema enforcing string length and email patterns.

### 2. Qubits
Defines active hardware physical qubits (e.g. Q0, Q1, Q2):
- **Indexes**: Unique index on `qubit_id`.
- **Fields**: `qubit_id`, `status` (active, dead, calibration_required), `created_at`, `updated_at`.

### 3. CalibrationHistory
Time-series collection mapping physical calibration drift logs:
- **Indexes**: Compound index on `(qubit_id, timestamp)`.
- **Fields**: `qubit_id` (links to Qubits), `readout_error`, `t1`, `t2`, `gate_error_1q`, `gate_error_2q`, `frequency`, `anharmonicity`, `timestamp`.

### 4. APIHistory
Audit logs tracking api usage:
- **Indexes**: TTL Index on `timestamp` expiring after 30 days (`2592000` seconds).
