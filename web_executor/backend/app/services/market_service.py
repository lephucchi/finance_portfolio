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

            # TODO: Cache disabled until Supabase cache tables are verified
            # Supabase cache layer may not be fully initialized
            # Restore these lines once tables are set up:
            # query_hash = self._hash_query(sql)
            # cached = self.supabase.get_cached_result(query_hash)
            # if cached:
            #     logger.info("Returning cached market data")
            #     return cached["result"]

            # Execute query directly
            logger.info(f"Fetching market data from {start_date} to {end_date}")
            logger.info(f"SQL Query: {sql}")
            results = self.athena.query(sql)
            
            if not results:
                logger.warning(f"No data found for date range {start_date} to {end_date}")
                return []
            
            logger.info(f"Query returned {len(results)} rows")

            # TODO: Cache results when Supabase is available
            # Restore this when cache is ready:
            # query_hash = self._hash_query(sql)
            # self.supabase.cache_result(query_hash, sql, results)

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
                    AND partition_date >= '{start_date}' 
                    AND partition_date <= '{end_date}'
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
        
        NOTE: This table does not exist in fizbert database yet.
        Available tables: macro_features, market_dashboard, risk_metrics, sentiment_features

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            list: Sector performance data (currently returns empty list)
        """
        try:
            # TODO: Table fizbert.sector_performance does not exist
            # Need to create this table in Gold layer or compute from market_dashboard
            logger.warning("sector_performance table does not exist in fizbert database")
            
            # Return empty result for now
            return []
            
            # Original query (commented out until table is created):
            # sql = f"""
            #     SELECT 
            #         data_date,
            #         sector,
            #         avg_price_change_pct,
            #         avg_volatility
            #     FROM fizbert.sector_performance
            #     WHERE data_date BETWEEN DATE '{start_date}' AND DATE '{end_date}'
            #     ORDER BY data_date DESC
            # """
            # 
            # logger.info("Fetching sector performance data")
            # return self.athena.query(sql)

        except Exception as e:
            logger.error(f"Failed to get sector performance: {str(e)}")
            raise

    def debug_check_available_data(self) -> dict[str, Any]:
        """
        Debug method to check what data is available in market_dashboard.
        
        Returns:
            dict: Information about available data
        """
        try:
            # Get date range
            date_range_sql = """
                SELECT 
                    MIN(data_date) as min_date,
                    MAX(data_date) as max_date,
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT symbol) as unique_symbols,
                    COUNT(DISTINCT data_date) as unique_dates
                FROM fizbert.market_dashboard
            """
            
            # Get sample data
            sample_sql = """
                SELECT 
                    symbol,
                    data_date,
                    close,
                    volume
                FROM fizbert.market_dashboard
                ORDER BY data_date DESC
                LIMIT 10
            """
            
            # Get distinct dates (last 30 days)
            dates_sql = """
                SELECT DISTINCT data_date
                FROM fizbert.market_dashboard
                ORDER BY data_date DESC
                LIMIT 30
            """
            
            # Check partitions
            partitions_sql = """
                SELECT DISTINCT partition_date
                FROM fizbert.market_dashboard
                ORDER BY partition_date DESC
                LIMIT 20
            """
            
            logger.info("Fetching debug information")
            date_info = self.athena.query(date_range_sql)
            sample_data = self.athena.query(sample_sql)
            available_dates = self.athena.query(dates_sql)
            partitions = self.athena.query(partitions_sql)
            
            return {
                "date_range": date_info[0] if date_info else {},
                "sample_data": sample_data,
                "recent_dates": [d.get('data_date') for d in available_dates],
                "recent_partitions": [p.get('partition_date') for p in partitions],
                "note": "Check if data_date matches partition_date for new data"
            }
            
        except Exception as e:
            logger.error(f"Failed to check available data: {str(e)}")
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

        # NOTE: Using partition_date instead of data_date because:
        # - Data is partitioned by date (partition_date)
        # - data_date may not match partition_date in some cases
        # - This ensures we query the correct partitions
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
            WHERE partition_date >= '{start_date}' 
                AND partition_date <= '{end_date}'
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
