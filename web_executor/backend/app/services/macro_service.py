"""
Macro economic data service - handles macro indicators queries.
"""

import hashlib
from datetime import date
from typing import Any, Optional

from app.core.config import get_logger
from app.db import AthenaClient, SupabaseClient

logger = get_logger(__name__)


class MacroService:
    """
    Macro economic service.
    Manages macro indicators and economic data.
    
    SOLID Principles:
    - Single Responsibility: Only handles macro data operations
    - Dependency Inversion: Takes database clients as dependencies
    """

    def __init__(self, athena_client: AthenaClient, supabase_client: SupabaseClient):
        """
        Initialize macro service.

        Args:
            athena_client: Athena client instance
            supabase_client: Supabase client instance
        """
        self.athena = athena_client
        self.supabase = supabase_client

    def get_macro_indicators(
        self,
        start_date: date,
        end_date: date,
        indicators: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        """
        Get macro economic indicators.

        Args:
            start_date: Start date
            end_date: End date
            indicators: Optional list of specific indicators to fetch

        Returns:
            list: Macro indicator data
        """
        try:
            indicator_filter = ""
            if indicators:
                indicator_list = ", ".join([f"'{ind}'" for ind in indicators])
                indicator_filter = f"AND indicator_name IN ({indicator_list})"

            sql = f"""
                SELECT 
                    data_date,
                    indicator_name,
                    indicator_value,
                    ma_7,
                    ma_30
                FROM fizbert.macro_features
                WHERE partition_date >= '{start_date}' 
                    AND partition_date <= '{end_date}'
                    {indicator_filter}
                ORDER BY data_date DESC, indicator_name
            """

            # Check cache
            query_hash = self._hash_query(sql)
            cached = self.supabase.get_cached_result(query_hash)
            if cached:
                logger.info("Returning cached macro indicators")
                return cached["result"]

            logger.info(f"Fetching macro indicators from {start_date} to {end_date}")
            results = self.athena.query(sql)

            # Cache results
            self.supabase.cache_result(query_hash, sql, results)

            return results

        except Exception as e:
            logger.error(f"Failed to get macro indicators: {str(e)}")
            raise

    def get_available_indicators(self) -> list[str]:
        """
        Get list of available macro indicators.

        Returns:
            list: Available indicator names
        """
        try:
            sql = """
                SELECT DISTINCT indicator_name
                FROM fizbert.macro_features
                ORDER BY indicator_name
            """

            logger.info("Fetching available indicators")
            results = self.athena.query(sql)
            return [r["indicator_name"] for r in results]

        except Exception as e:
            logger.error(f"Failed to get available indicators: {str(e)}")
            raise

    def get_indicator_time_series(
        self,
        indicator_name: str,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        """
        Get time series for specific indicator.

        Args:
            indicator_name: Indicator name (e.g., GDP, CPI, USD/VND)
            start_date: Start date
            end_date: End date

        Returns:
            list: Time series data
        """
        try:
            sql = f"""
                SELECT 
                    data_date,
                    indicator_value,
                    ma_7,
                    ma_30
                FROM fizbert.macro_features
                WHERE indicator_name = '{indicator_name}'
                    AND partition_date >= '{start_date}' 
                    AND partition_date <= '{end_date}'
                ORDER BY data_date DESC
            """

            logger.info(f"Fetching time series for {indicator_name}")
            return self.athena.query(sql)

        except Exception as e:
            logger.error(f"Failed to get indicator time series: {str(e)}")
            raise

    def get_forex_rates(
        self,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        """
        Get exchange rate data (USD/VND, EUR/VND, etc).

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            list: Exchange rate data
        """
        try:
            sql = f"""
                SELECT 
                    data_date,
                    indicator_name,
                    indicator_value
                FROM fizbert.macro_features
                WHERE indicator_name LIKE '%VND'
                    AND partition_date >= '{start_date}' 
                    AND partition_date <= '{end_date}'
                ORDER BY data_date DESC
            """

            logger.info("Fetching forex rates")
            return self.athena.query(sql)

        except Exception as e:
            logger.error(f"Failed to get forex rates: {str(e)}")
            raise

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
