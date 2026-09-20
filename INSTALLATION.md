# TwinQ-Map Installation and Execution Guide

This document describes how to install dependencies and execute the TwinQ-Map application console locally.

## 1. Prerequisites
- **Python**: Version 3.10 or higher.
- **Node.js**: Version 20 or higher.
- **MongoDB**: Standalone community server or Mongo Atlas URI.

---

## 2. Backend Setup
1. Open terminal and navigate to the project directory:
   ```bash
   cd TwinQ-Map
   ```
2. Configure settings inside `backend/.env`. Example:
   ```env
   MONGO_URI=mongodb://localhost:27017/twinq_map
   SECRET_KEY=super_secret_encryption_key_hash_salt
   ENVIRONMENT=development
   OPERATION_MODE=SIMULATED
   ```
3. Install backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Seed and generate datasets (1Q to 5Q, 100 epochs):
   ```bash
   python -c "from backend.mathematical_quantum_simulator.dataset_generator import DatasetGenerator; DatasetGenerator().generate_all_datasets()"
   ```
5. Run the FastAPI backend:
   ```bash
   python -m backend.main
   ```
   The backend server will start listening at `http://localhost:8000`. Swagger API documentation is available at `http://localhost:8000/api/v1/docs`.

---

## 3. Frontend Setup
1. In a new terminal, navigate to the `frontend/` directory:
   ```bash
   cd TwinQ-Map/frontend
   ```
2. Install client dependencies (use legacy peer deps flag due to React Three Fiber conflicts):
   ```bash
   npm install --legacy-peer-deps
   ```
3. Compile production Vite build:
   ```bash
   npm run build
   ```
4. Start the frontend React app in development mode:
   ```bash
   npm run dev
   ```
   The console will launch at `http://localhost:3000`.

---

## 4. Run Pytest Suite
To run all unit and integration test assertions:
```bash
cd TwinQ-Map
python -m pytest backend/tests/
```
