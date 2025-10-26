"""
Pydantic schemas for request/response validation.
"""

from datetime import date, datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# ========================
# GENERIC RESPONSE SCHEMAS
# ========================


class PaginationModel(BaseModel):
    """Pagination metadata."""

    page: int = Field(gt=0, description="Page number")
    page_size: int = Field(gt=0, description="Items per page")
    total_items: int = Field(ge=0, description="Total items count")
    total_pages: int = Field(ge=0, description="Total pages count")


class ResponseModel(BaseModel, Generic[T]):
    """
    Generic response model with metadata.
    """

    success: bool = Field(True, description="Request success status")
    data: T = Field(description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    pagination: Optional[PaginationModel] = Field(None, description="Pagination info")


class ErrorResponseModel(BaseModel):
    """Error response model."""

    success: bool = Field(False, description="Request success status")
    error: str = Field(description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ========================
# MARKET DATA SCHEMAS
# ========================


class StockDataResponse(BaseModel):
    """Stock market data response."""

    symbol: str = Field(description="Stock ticker symbol")
    data_date: Optional[date] = Field(None, description="Trading date")
    open: Optional[float] = Field(None, description="Opening price")
    high: Optional[float] = Field(None, description="Highest price")
    low: Optional[float] = Field(None, description="Lowest price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")
    price_change: Optional[float] = Field(None, description="Absolute price change")
    price_change_pct: float = Field(description="Percentage price change")
    ma_5: Optional[float] = Field(None, description="5-day moving average")
    ma_10: Optional[float] = Field(None, description="10-day moving average")
    ma_20: Optional[float] = Field(None, description="20-day moving average")
    rsi_14: Optional[float] = Field(None, description="14-day RSI")
    volatility_7d: Optional[float] = Field(None, description="7-day volatility")


class MarketDashboardRequest(BaseModel):
    """Market dashboard query request."""

    start_date: date = Field(description="Start date")
    end_date: date = Field(description="End date")
    symbols: Optional[list[str]] = Field(None, description="Stock symbols filter")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


# ========================
# SENTIMENT ANALYSIS SCHEMAS
# ========================


class SentimentDataResponse(BaseModel):
    """Sentiment analysis data response."""

    data_date: date = Field(description="Analysis date")
    total_articles: int = Field(description="Total articles count")
    avg_sentiment: float = Field(description="Average sentiment score")
    positive_count: int = Field(description="Positive articles count")
    negative_count: int = Field(description="Negative articles count")
    neutral_count: Optional[int] = Field(None, description="Neutral articles count")


class NewsArticleResponse(BaseModel):
    """Individual news article response."""

    id: str = Field(description="Article ID")
    data_date: date = Field(description="Article date")
    title: str = Field(description="Article title")
    source: str = Field(description="News source")
    sentiment_score: float = Field(description="Sentiment score (-1 to 1)")
    link: Optional[str] = Field(None, description="Article URL")


class SentimentDashboardRequest(BaseModel):
    """Sentiment dashboard query request."""

    start_date: date = Field(description="Start date")
    end_date: date = Field(description="End date")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


# ========================
# MACRO DATA SCHEMAS
# ========================


class MacroIndicatorResponse(BaseModel):
    """Macro economic indicator response."""

    data_date: date = Field(description="Indicator date")
    indicator_name: str = Field(description="Indicator name")
    indicator_value: float = Field(description="Indicator value")
    ma_7: Optional[float] = Field(None, description="7-day moving average")
    ma_30: Optional[float] = Field(None, description="30-day moving average")


class MacroDashboardRequest(BaseModel):
    """Macro dashboard query request."""

    start_date: date = Field(description="Start date")
    end_date: date = Field(description="End date")
    indicators: Optional[list[str]] = Field(None, description="Specific indicators to fetch")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


# ========================
# HEALTH CHECK SCHEMAS
# ========================


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="Service status")
    version: str = Field(description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database: dict[str, Any] = Field(description="Database connection status")


# ========================
# ANALYTICS SCHEMAS
# ========================


class DashboardSummaryResponse(BaseModel):
    """Overall dashboard summary."""

    total_stocks: int = Field(default=0, description="Total stocks tracked")
    market_change_pct: float = Field(default=0.0, description="Market change percentage")
    avg_sentiment: float = Field(default=0.0, description="Average market sentiment")
    top_gainers: list[StockDataResponse] = Field(default_factory=list, description="Top gaining stocks")
    top_losers: list[StockDataResponse] = Field(default_factory=list, description="Top losing stocks")
    latest_update: Optional[datetime] = Field(default=None, description="Last data update time")
