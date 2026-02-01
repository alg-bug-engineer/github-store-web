"""
Data Service Health Check API

This service provides a minimal health check endpoint for the data service.
The main responsibility of data-service is to:
1. Run database migrations (via Alembic)
2. Run background sync tasks (via Celery)
3. Initialize system configuration on startup
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.db.session import SessionLocal
from app.db.initial_data import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database with seed data on startup."""
    logger.info("Initializing database with seed data...")
    db = SessionLocal()
    try:
        init_db(db)
        logger.info("Database initialization completed.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Data Service Health Check API",
    version="1.0.0",
    lifespan=lifespan,
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
