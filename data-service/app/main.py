"""
Data Service Health Check API

This service provides a minimal health check endpoint for the data service.
The main responsibility of data-service is to:
1. Run database migrations (via Alembic)
2. Run background sync tasks (via Celery)
"""
import logging
from fastapi import FastAPI
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Data Service Health Check API",
    version="1.0.0",
)


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "service": "data-service",
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "GitHub Data Service",
        "description": "Responsible for data fetching, migrations, and background sync tasks",
    }
