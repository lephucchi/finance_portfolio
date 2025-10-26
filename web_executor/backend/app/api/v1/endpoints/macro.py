"""Macro economic data endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import get_logger
from app.db import AthenaClient, SupabaseClient
from app.schemas import ResponseModel
from app.services import MacroService

logger = get_logger(__name__)
router = APIRouter()


def get_macro_service() -> MacroService:
    """Get macro service instance."""
    athena = AthenaClient()
    supabase = SupabaseClient()
    return MacroService(athena, supabase)


@router.get(
    "/indicators",
    summary="Get macro indicators",
    description="Get macro economic indicators",
)
async def get_macro_indicators(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    indicators: str = Query(None, description="Comma-separated indicator names"),
    service: MacroService = Depends(get_macro_service),
) -> ResponseModel:
    """
    Get macro indicators.
    
    Args:
        start_date: Start date
        end_date: End date
        indicators: Comma-separated indicator names (optional)
        service: Macro service instance
        
    Returns:
        ResponseModel: Macro indicators data
    """
    try:
        indicator_list = indicators.split(",") if indicators else None
        data = service.get_macro_indicators(start_date, end_date, indicator_list)

        return ResponseModel(
            success=True,
            data=data,
            message="Macro indicators retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Failed to get macro indicators: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/available-indicators",
    summary="Get available indicators",
    description="Get list of available macro indicators",
)
async def get_available_indicators(
    service: MacroService = Depends(get_macro_service),
) -> ResponseModel:
    """
    Get available indicators.
    
    Args:
        service: Macro service instance
        
    Returns:
        ResponseModel: List of available indicators
    """
    try:
        data = service.get_available_indicators()

        return ResponseModel(
            success=True,
            data=data,
            message="Available indicators retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Failed to get available indicators: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/indicator/{indicator_name}",
    summary="Get indicator time series",
    description="Get time series data for a specific indicator",
)
async def get_indicator_time_series(
    indicator_name: str,
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    service: MacroService = Depends(get_macro_service),
) -> ResponseModel:
    """
    Get indicator time series.
    
    Args:
        indicator_name: Indicator name
        start_date: Start date
        end_date: End date
        service: Macro service instance
        
    Returns:
        ResponseModel: Time series data
    """
    try:
        data = service.get_indicator_time_series(indicator_name, start_date, end_date)

        return ResponseModel(
            success=True,
            data=data,
            message="Indicator time series retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Failed to get indicator time series: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/forex",
    summary="Get forex rates",
    description="Get exchange rate data (USD/VND, EUR/VND, etc)",
)
async def get_forex_rates(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    service: MacroService = Depends(get_macro_service),
) -> ResponseModel:
    """
    Get forex rates.
    
    Args:
        start_date: Start date
        end_date: End date
        service: Macro service instance
        
    Returns:
        ResponseModel: Forex rates data
    """
    try:
        data = service.get_forex_rates(start_date, end_date)

        return ResponseModel(
            success=True,
            data=data,
            message="Forex rates retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Failed to get forex rates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
