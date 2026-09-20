# API Reference documentation

The TwinQ-Map FastAPI service exposes REST endpoints structured under the prefix `/api/v1`.

## 1. Authentication Endpoints
- **POST `/auth/register`**: Creates a new user record.
- **POST `/auth/login`**: JSON-based credentials authorization. Returns JWT token.
- **POST `/auth/token`**: OAuth2 standard form-based login. Returns JWT token.
- **POST `/auth/refresh`**: Generates a new JWT token.
- **GET `/auth/me`**: Fetches the currently active authenticated user object.

## 2. Digital Twin Endpoints
- **GET `/digital-twin/{qubit_id}`**: Retrieves current twin snapshot.
- **POST `/digital-twin/sync`**: Synchronizes new physical calibration data into twin lineage history stack.
- **POST `/digital-twin/rollback`**: Truncates history to restore a target version.
- **GET `/digital-twin/analytics/summary`**: Computes hardware stability metrics.

## 3. Adaptive Scheduler
- **POST `/scheduler/schedule`**: Maps a logical coupling constraint graph onto physical hardware.
- **GET `/scheduler/health-indices`**: Computes QHI health indexes.

## 4. Calibration & Execution
- **POST `/calibrations/insert`**: Inserts a new calibration document.
- **GET `/calibrations/history`**: Paginated/sorted query lists.
- **POST `/quantum/execute`**: Executes circuit representation mathematically.
- **GET `/quantum/device-status`**: Queries hardware simulator status.
