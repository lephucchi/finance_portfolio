"""
Market data service - handles stock market queries and analysis.
"""

import hashlib
from datetime import date
from typing import Any, Optional

from app.core.config import get_logger
from app.db import AthenaClient, SupabaseClient
from app.schemas import StockDataResponse

logger = get_logger(__name__)


class MarketService:
    """
    Market data service.
    Manages stock market data queries and caching.
    
    SOLID Principles:
    - Single Responsibility: Only handles market data operations
    - Dependency Inversion: Takes Athena and Supabase clients as dependencies
    - Open/Closed: Can be extended for new market data types
    """

    def __init__(self, athena_client: AthenaClient, supabase_client: SupabaseClient):
        """
        Initialize market service.

        Args:
            athena_client: Athena client instance
            supabase_client: Supabase client instance
        """
        self.athena = athena_client
        self.supabase = supabase_client

    def get_stock_data(
        self,
        start_date: date,
        end_date: date,
        symbols: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        """
        Get stock market data.

        Args:
            start_date: Start date for query
            end_date: End date for query
            symbols: Optional list of symbols to filter

        Returns:
            list: Stock data records
        """
        try:
            # Build query
            sql = self._build_market_query(start_date, end_date, symbols)

            # Check cache
            query_hash = self._hash_query(sql)
            cached = self.supabase.get_cached_result(query_hash)
            if cached:
                logger.info("Returning cached market data")
                return cached["result"]

            # Execute query
            logger.info(f"Fetching market data from {start_date} to {end_date}")
            results = self.athena.query(sql)

            # Cache results
            self.supabase.cache_result(query_hash, sql, results)

            return results

        except Exception as e:
            logger.error(f"Failed to get stock data: {str(e)}")
            raise

    def get_technical_indicators(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        """
        Get technical indicators for a stock.

        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date

        Returns:
            list: Technical indicators data
        """
        try:
            sql = f"""
                SELECT 
                    symbol,
                    data_date,
                    close,
                    ma_20,
                    rsi_14,
                    volatility_7d
                FROM fizbert.market_dashboard
                WHERE symbol = '{symbol}'
                    AND partition_date BETWEEN '{start_date}' AND '{end_date}'
                ORDER BY data_date DESC
            """

            logger.info(f"Fetching technical indicators for {symbol}")
            return self.athena.query(sql)

        except Exception as e:
            logger.error(f"Failed to get technical indicators: {str(e)}")
            raise

    def get_sector_performance(
        self,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        """
        Get sector performance data.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            list: Sector performance data
        """
        try:
            sql = f"""
                SELECT 
                    data_date,
                    sector,
                    avg_price_change_pct,
                    avg_volatility
                FROM fizbert.sector_performance
                WHERE partition_date BETWEEN '{start_date}' AND '{end_date}'
                ORDER BY data_date DESC
            """

            logger.info("Fetching sector performance data")
            return self.athena.query(sql)

        except Exception as e:
            logger.error(f"Failed to get sector performance: {str(e)}")
            raise

    def _build_market_query(
        self,
        start_date: date,
        end_date: date,
        symbols: Optional[list[str]] = None,
    ) -> str:
        """
        Build SQL query for market data.

        Args:
            start_date: Start date
            end_date: End date
            symbols: Optional list of symbols

        Returns:
            str: SQL query
        """
        symbol_filter = ""
        if symbols:
            symbol_list = ", ".join([f"'{s}'" for s in symbols])
            symbol_filter = f"AND symbol IN ({symbol_list})"

        sql = f"""
            SELECT 
                symbol,
                data_date,
                open,
                close,
                volume,
                price_change_pct,
                ma_20,
                rsi_14,
                volatility_7d
            FROM fizbert.market_dashboard
            WHERE partition_date BETWEEN '{start_date}' AND '{end_date}'
                {symbol_filter}
            ORDER BY data_date DESC, symbol
        """

        return sql

    @staticmethod
    def _hash_query(query: str) -> str:
        """
        Generate hash for query.

        Args:
            query: SQL query

        Returns:
            str: Query hash
        """
        return hashlib.sha256(query.encode()).hexdigest()
