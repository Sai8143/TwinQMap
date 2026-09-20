# Docker Containerization Guide

This document describes how to deploy and run TwinQ-Map using Docker containers.

## 1. Local Development Run
To build and run all services (FastAPI, React web app, and MongoDB community server) locally using Docker Compose:
1. Ensure Docker Desktop is active.
2. Build and launch:
   ```bash
   docker-compose up --build
   ```
3. Once the database health checks verify readiness, the containers start listening:
   - **Frontend Console Dashboard**: `http://localhost:3000`
   - **Backend API Swagger**: `http://localhost:8000/api/v1/docs`
   - **MongoDB Connection Port**: `mongodb://localhost:27017`

---

## 2. Production Stack Services
- **mongodb**: Runs community server with mapped database persistence storage volume.
- **backend**: Runs the Python environment container with volume mapping for Rotating loggers under `/app/logs`.
- **frontend**: React client built, bundled, and served using an Nginx alpine container.
