import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import settings
from backend.database.connection import MongoDBManager
from backend.database.collections import initialize_collections
from backend.middlewares.error_handler import GlobalErrorHandlerMiddleware
from backend.core.logging import general_logger
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager managing the startup and shutdown lifecycles.
    """
    general_logger.info("Initializing TwinQ-Map service lifecycle...")
    
    # 1. Initialize MongoDB connection
    await MongoDBManager.connect()
    
    # 2. Setup indices and validations on collections
    db = MongoDBManager.get_database()
    await initialize_collections(db)
    
    yield
    
    # 3. Clean up database connection
    await MongoDBManager.disconnect()
    general_logger.info("TwinQ-Map service shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Dynamic Digital Twin–Driven Predictive Qubit Mapping for Time-Varying NISQ Processors API Interface.",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Interceptor Middleware
app.add_middleware(GlobalErrorHandlerMiddleware)

from backend.middlewares.rate_limiter import SimpleRateLimiterMiddleware
app.add_middleware(SimpleRateLimiterMiddleware, limit=120)

@app.get("/", tags=["Monitoring"])
async def root():
    return {
        "message": "TwinQ-Map API Server Live",
        "docs": f"{settings.API_V1_STR}/docs",
        "health": f"{settings.API_V1_STR}/health"
    }

@app.get("/health", tags=["Monitoring"])
@app.get("/api/v1/health", tags=["Monitoring"])
async def health_check():
    """
    Liveness and database readiness probe.
    """
    status = "healthy"
    db_status = "connected"
    
    try:
        db = MongoDBManager.get_database()
        await db.command('ping')
    except Exception:
        status = "degraded"
        db_status = "disconnected"
        
    return {
        "status": status,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "mode": settings.OPERATION_MODE
    }

from backend.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
