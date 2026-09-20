# Installation Guide

Follow these steps to deploy and run **TwinQ-Map** locally or in production.

## System Prerequisites
- **Python**: v3.12+
- **NodeJS**: v20+ (with npm/yarn)
- **MongoDB**: v7.0+ (Community or Atlas)

## Backend Initialization
1. Clone the project and navigate to the backend directory:
   ```bash
   cd TwinQ-Map/backend
   ```
2. Create and activate a python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template and customize key secrets:
   ```bash
   cp .env.example .env
   ```
5. Spin up the FastAPI server via Uvicorn:
   ```bash
   python main.py
   ```
   The backend API will listen at `http://localhost:8000`. You can inspect the Swagger OpenAPI specification at `http://localhost:8000/api/v1/docs`.

## Frontend Initialization
1. Navigate to the frontend directory:
   ```bash
   cd TwinQ-Map/frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Run the hot-reloading development server:
   ```bash
   npm run dev
   ```
   The Vite local dev application will open at `http://localhost:5173`.
