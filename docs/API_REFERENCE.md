# API Reference Documentation

All endpoints are prefixed with `/api/v1` and require header parameters: `Authorization: Bearer <JWT_TOKEN>`.

## REST API Details

### 1. Digital Twin Operations

#### Create Twin
- **URL**: `/api/v1/digital-twin`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "qubit_id": "Q0",
    "status": "Dormant",
    "metadata": {}
  }
  ```
- **Response**: `201 Created`

#### Get Twin
- **URL**: `/api/v1/digital-twin/{qubit_id}`
- **Method**: `GET`
- **Response**: `200 OK` Twin state.

#### Update Twin
- **URL**: `/api/v1/digital-twin/{qubit_id}`
- **Method**: `PUT`
- **Payload**:
  ```json
  {
    "status": "Active",
    "metadata": {"recalibrated": true}
  }
  ```
- **Response**: `200 OK`

#### Soft Delete Twin
- **URL**: `/api/v1/digital-twin/{qubit_id}`
- **Method**: `DELETE`
- **Response**: `204 No Content`

#### Get Twin History Buffer
- **URL**: `/api/v1/digital-twin/{qubit_id}/history`
- **Method**: `GET`
- **Parameters**: `limit` (default 50)
- **Response**: `200 OK` Rolling list of calibrations.

#### Get Twin Version History
- **URL**: `/api/v1/digital-twin/{qubit_id}/versions`
- **Method**: `GET`
- **Parameters**: `limit`, `skip`
- **Response**: `200 OK` List of Twin Version snapshots.

#### Synchronize Twin
- **URL**: `/api/v1/digital-twin/{qubit_id}/sync`
- **Method**: `POST`
- **Parameters**: `is_full_sync` (bool)
- **Response**: `200 OK` Synchronized Twin state.

#### Rollback Twin
- **URL**: `/api/v1/digital-twin/{qubit_id}/rollback`
- **Method**: `POST`
- **Parameters**: `target_version` (int)
- **Response**: `200 OK`

#### Twin Analytics
- **URL**: `/api/v1/digital-twin/{qubit_id}/analytics`
- **Method**: `GET`
- **Response**: `200 OK` Drift statistics, coherence/frequency trends, and stability.

---

### 2. Quantum Calibration History

#### Insert Calibration
- **URL**: `/api/v1/quantum/calibration`
- **Method**: `POST`
- **Payload**: Calibration DTO
- **Response**: `201 Created`

#### Get Calibration History
- **URL**: `/api/v1/quantum/calibration/history`
- **Method**: `GET`
- **Parameters**: `qubit_id`, `limit`, `skip`
- **Response**: `200 OK`
