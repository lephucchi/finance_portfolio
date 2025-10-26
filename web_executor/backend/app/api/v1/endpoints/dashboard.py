"""Dashboard endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import get_logger
from app.db import AthenaClient, SupabaseClient
from app.schemas import ResponseModel, DashboardSummaryResponse
from app.services import AnalyticsService

logger = get_logger(__name__)
router = APIRouter()


def get_analytics_service() -> AnalyticsService:
    """Get analytics service instance."""
    athena = AthenaClient()
    supabase = SupabaseClient()
    return AnalyticsService(athena, supabase)


@router.get(
    "/summary",
    response_model=ResponseModel[DashboardSummaryResponse],
    summary="Get dashboard summary",
    description="Get overall dashboard summary for a specific date",
)
async def get_dashboard_summary(
    date_: date = Query(None, description="Query date (defaults to today)"),
    service: AnalyticsService = Depends(get_analytics_service),
) -> ResponseModel[DashboardSummaryResponse]:
    """
    Get dashboard summary.
    
    Args:
        date_: Query date
        service: Analytics service instance
        
    Returns:
        ResponseModel: Dashboard summary
    """
    try:
        if not date_:
            from datetime import datetime

            date_ = datetime.utcnow().date()

        summary = service.get_dashboard_summary(date_)

        return ResponseModel(
            success=True,
            data=summary,
            message="Dashboard summary retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Failed to get dashboard summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/correlation",
    summary="Get correlation analysis",
    description="Get correlation between sentiment, macro indicators, and market movement",
)
async def get_correlation_analysis(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    service: AnalyticsService = Depends(get_analytics_service),
) -> ResponseModel:
    """
    Get correlation analysis.
    
    Args:
        start_date: Start date
        end_date: End date
        service: Analytics service instance
        
    Returns:
        ResponseModel: Correlation analysis data
    """
    try:
        analysis = service.get_correlation_analysis(start_date, end_date)

        return ResponseModel(
            success=True,
            data=analysis,
            message="Correlation analysis retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Failed to get correlation analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
