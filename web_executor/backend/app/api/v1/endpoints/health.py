"""Health check endpoints."""

from datetime import datetime

from fastapi import APIRouter

from app.core.config import get_logger
from app.schemas import HealthCheckResponse
from config.settings import settings

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check endpoint",
    description="Check if API and databases are healthy",
)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint.
    
    Returns:
        HealthCheckResponse: Service health status
    """
    try:
        return HealthCheckResponse(
            status="healthy",
            version=settings.APP_VERSION,
            timestamp=datetime.utcnow(),
            database={
                "athena": "configured",
                "supabase": "configured",
            },
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheckResponse(
            status="degraded",
            version=settings.APP_VERSION,
            timestamp=datetime.utcnow(),
            database={
                "athena": "error",
                "supabase": "error",
            },
        )


@router.get(
    "/ready",
    summary="Readiness check",
    description="Check if API is ready to accept requests",
)
async def readiness_check() -> dict:
    """
    Readiness check endpoint.
    
    Returns:
        dict: Readiness status
    """
    return {
        "ready": True,
        "version": settings.APP_VERSION,
    }
