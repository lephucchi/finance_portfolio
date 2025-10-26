"""Market data endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import get_logger
from app.db import AthenaClient, SupabaseClient
from app.schemas import MarketDashboardRequest, ResponseModel, StockDataResponse
from app.services import MarketService

logger = get_logger(__name__)
router = APIRouter()


def get_market_service() -> MarketService:
    """Get market service instance."""
    athena = AthenaClient()
    supabase = SupabaseClient()
    return MarketService(athena, supabase)


@router.get(
    "/stocks",
    response_model=ResponseModel[list[StockDataResponse]],
    summary="Get stock data",
    description="Get stock market data for a date range",
)
async def get_stock_data(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    symbols: str = Query(None, description="Comma-separated stock symbols"),
    service: MarketService = Depends(get_market_service),
) -> ResponseModel[list[StockDataResponse]]:
    """
    Get stock market data.
    
    Args:
        start_date: Start date
        end_date: End date
        symbols: Comma-separated symbols (optional)
        service: Market service instance
        
    Returns:
        ResponseModel: Stock data
    """
    try:
        symbol_list = symbols.split(",") if symbols else None
        data = service.get_stock_data(start_date, end_date, symbol_list)

        return ResponseModel(
            success=True,
            data=data,
            message="Stock data retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Failed to get stock data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/technical-indicators",
    summary="Get technical indicators",
    description="Get technical indicators (MA, RSI, Volatility) for a stock",
)
async def get_technical_indicators(
    symbol: str = Query(..., description="Stock symbol"),
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    service: MarketService = Depends(get_market_service),
) -> ResponseModel:
    """
    Get technical indicators.
    
    Args:
        symbol: Stock symbol
        start_date: Start date
        end_date: End date
        service: Market service instance
        
    Returns:
        ResponseModel: Technical indicators data
    """
    try:
        data = service.get_technical_indicators(symbol, start_date, end_date)

        return ResponseModel(
            success=True,
            data=data,
            message="Technical indicators retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Failed to get technical indicators: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sector-performance",
    summary="Get sector performance",
    description="Get sector performance analysis",
)
async def get_sector_performance(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    service: MarketService = Depends(get_market_service),
) -> ResponseModel:
    """
    Get sector performance.
    
    Args:
        start_date: Start date
        end_date: End date
        service: Market service instance
        
    Returns:
        ResponseModel: Sector performance data
    """
    try:
        data = service.get_sector_performance(start_date, end_date)

        return ResponseModel(
            success=True,
            data=data,
            message="Sector performance retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Failed to get sector performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
