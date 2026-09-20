# Production Deployment Guide

This guide describes how to deploy TwinQ-Map on production cloud hosts.

## 1. MongoDB Atlas Setup
1. Create a free cluster on MongoDB Atlas.
2. Under Network Access, whitelist the deployment server IPs (or allow 0.0.0.0/0 temporarily).
3. Create a database user and copy the connection string. Example:
   ```env
   MONGO_URI=mongodb+srv://user:pass@twinq.mongodb.net/twinq_map?retryWrites=true&w=majority
   ```

---

## 2. Deploying Backend on Render or Railway
1. Create a new Web Service linked to the Github Repository.
2. Build Settings:
   - Environment: Python 3.10
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 10000`
3. Environment Variables:
   - Configure `MONGO_URI`, `SECRET_KEY`, `ENVIRONMENT=production`, and `OPERATION_MODE=SIMULATED` (or configure hardware API tokens).

---

## 3. Deploying Frontend on Vercel or Netlify
1. Create a new project linked to the Github Repository.
2. Root Directory: `frontend`
3. Build Settings:
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Configure API Proxy:
   - For Vercel, define `vercel.json` redirects to route `/api/v1/:path*` to the backend Render/Railway endpoint URL.
