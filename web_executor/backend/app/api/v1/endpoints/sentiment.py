"""Sentiment analysis endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import get_logger
from app.db import AthenaClient, SupabaseClient
from app.schemas import ResponseModel
from app.services import SentimentService

logger = get_logger(__name__)
router = APIRouter()


def get_sentiment_service() -> SentimentService:
    """Get sentiment service instance."""
    athena = AthenaClient()
    supabase = SupabaseClient()
    return SentimentService(athena, supabase)


@router.get(
    "/summary",
    summary="Get sentiment summary",
    description="Get daily sentiment summary",
)
async def get_sentiment_summary(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    service: SentimentService = Depends(get_sentiment_service),
) -> ResponseModel:
    """
    Get sentiment summary.
    
    Args:
        start_date: Start date
        end_date: End date
        service: Sentiment service instance
        
    Returns:
        ResponseModel: Sentiment summary data
    """
    try:
        data = service.get_sentiment_summary(start_date, end_date)

        return ResponseModel(
            success=True,
            data=data,
            message="Sentiment summary retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Failed to get sentiment summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/articles",
    summary="Get news articles",
    description="Get news articles with sentiment analysis",
)
async def get_news_articles(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    sentiment: str = Query(None, description="Filter by sentiment (positive, negative, neutral)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of articles"),
    service: SentimentService = Depends(get_sentiment_service),
) -> ResponseModel:
    """
    Get news articles.
    
    Args:
        start_date: Start date
        end_date: End date
        sentiment: Sentiment filter
        limit: Maximum number of articles
        service: Sentiment service instance
        
    Returns:
        ResponseModel: News articles
    """
    try:
        data = service.get_news_articles(start_date, end_date, sentiment, limit)

        return ResponseModel(
            success=True,
            data=data,
            message="News articles retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Failed to get news articles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/trend",
    summary="Get sentiment trend",
    description="Get sentiment trend over time (daily, weekly, or monthly)",
)
async def get_sentiment_trend(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    interval: str = Query("daily", description="Time interval (daily, weekly, monthly)"),
    service: SentimentService = Depends(get_sentiment_service),
) -> ResponseModel:
    """
    Get sentiment trend.
    
    Args:
        start_date: Start date
        end_date: End date
        interval: Time interval
        service: Sentiment service instance
        
    Returns:
        ResponseModel: Sentiment trend data
    """
    try:
        if interval not in ["daily", "weekly", "monthly"]:
            raise ValueError("Interval must be 'daily', 'weekly', or 'monthly'")

        data = service.get_sentiment_trend(start_date, end_date, interval)

        return ResponseModel(
            success=True,
            data=data,
            message="Sentiment trend retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Failed to get sentiment trend: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
