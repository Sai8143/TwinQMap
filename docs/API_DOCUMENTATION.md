# API Reference Documentation

All endpoints are prefixed with `/api/v1` by default and utilize JSON formats for payload communications.

## 1. Authentication Endpoints

### Register User
- **URL**: `/api/v1/auth/register`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "username": "quantum_dev",
    "email": "dev@twinqmap.org",
    "password": "securepassword123",
    "role": "researcher"
  }
  ```
- **Response**: `201 Created` with `UserResponse` DTO structure.

### Login / Authenticate
- **URL**: `/api/v1/auth/login`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "username": "quantum_dev",
    "password": "securepassword123"
  }
  ```
- **Response**: `200 OK` returning `access_token` and roles scope.

---

## 2. Quantum Operations

### Get Calibrations
- **URL**: `/api/v1/quantum/calibration`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <JWT_TOKEN>`
- **Response**: `200 OK` list containing decayed physical qubit coherence parameters.

### Execute Circuit
- **URL**: `/api/v1/quantum/execute`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <JWT_TOKEN>` (Researcher Role Required)
- **Parameters**:
  - `mapping`: List of physical mapping indices (e.g. `[0, 1, 3]`).
  - `shots`: Trial counts (default `1024`).
- **Response**: `202 Accepted` job ID and predicted fidelity details.
