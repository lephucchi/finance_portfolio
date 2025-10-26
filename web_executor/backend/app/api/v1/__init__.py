"""API v1 routes initialization."""

from fastapi import APIRouter

from .endpoints import dashboard, market, sentiment, macro, health

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include endpoint routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(market.router, prefix="/market", tags=["Market"])
api_router.include_router(sentiment.router, prefix="/sentiment", tags=["Sentiment"])
api_router.include_router(macro.router, prefix="/macro", tags=["Macro"])

__all__ = ["api_router"]
