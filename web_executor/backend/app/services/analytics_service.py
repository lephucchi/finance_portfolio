"""
Analytics service - high-level analytics and insights.
"""

from datetime import date, datetime
from typing import Any

from app.core.config import get_logger
from app.db import AthenaClient, SupabaseClient

logger = get_logger(__name__)


class AnalyticsService:
    """
    Analytics service.
    Provides high-level analytics and dashboard insights.
    
    SOLID Principles:
    - Single Responsibility: Only handles analytics operations
    - Dependency Inversion: Takes database clients as dependencies
    - Composition over Inheritance: Uses other services via dependency
    """

    def __init__(self, athena_client: AthenaClient, supabase_client: SupabaseClient):
        """
        Initialize analytics service.

        Args:
            athena_client: Athena client instance
            supabase_client: Supabase client instance
        """
        self.athena = athena_client
        self.supabase = supabase_client

    def get_dashboard_summary(
        self,
        date_: date,
    ) -> dict[str, Any]:
        """
        Get overall dashboard summary for a specific date.

        Args:
            date_: Query date

        Returns:
            dict: Dashboard summary data
        """
        try:
            logger.info(f"Generating dashboard summary for {date_}")

            # Get market stats
            market_stats = self._get_market_stats(date_)
            logger.info(f"Market stats: {market_stats}")

            # Get sentiment stats  
            sentiment_stats = self._get_sentiment_stats(date_)
            logger.info(f"Sentiment stats: {sentiment_stats}")

            # Get macro stats
            macro_stats = self._get_macro_stats(date_)
            logger.info(f"Macro stats: {macro_stats}")
            
            # Extract market values with defaults
            total_stocks = int(market_stats.get('total_stocks', 0)) if market_stats.get('total_stocks') else 0
            avg_market_change = float(market_stats.get('avg_market_change', 0.0)) if market_stats.get('avg_market_change') else 0.0
            total_volume = int(market_stats.get('total_volume', 0)) if market_stats.get('total_volume') else 0
            
            # Extract sentiment values with defaults
            avg_sentiment = float(sentiment_stats.get('avg_sentiment', 0.0)) if sentiment_stats.get('avg_sentiment') else 0.0
            positive_pct = float(sentiment_stats.get('positive_pct', 0.0)) if sentiment_stats.get('positive_pct') else 0.0
            article_count = int(sentiment_stats.get('article_count', 0)) if sentiment_stats.get('article_count') else 0

            # Get top gainers and losers
            top_gainers = self._get_top_movers(date_, direction='gainers', limit=5)
            top_losers = self._get_top_movers(date_, direction='losers', limit=5)
            
            # Get advancing/declining counts
            market_breadth = self._get_market_breadth(date_)

            # Extract macro indicators
            indicators = macro_stats.get('indicators', [])
            cpi = 0.0
            usd_vnd = 0.0
            for ind in indicators:
                if ind.get('indicator_name') == 'CPI':
                    cpi = float(ind.get('indicator_value', 0.0))
                elif ind.get('indicator_name') == 'USD_VND':
                    usd_vnd = float(ind.get('indicator_value', 0.0))

            # Format top gainers/losers
            formatted_gainers = [
                {
                    "symbol": g.get('symbol', ''),
                    "price_change_pct": g.get('price_change_pct', 0.0),
                    "close": g.get('close', 0.0),
                    "volume": g.get('volume', 0)
                }
                for g in top_gainers
            ]
            
            formatted_losers = [
                {
                    "symbol": l.get('symbol', ''),
                    "price_change_pct": l.get('price_change_pct', 0.0),
                    "close": l.get('close', 0.0),
                    "volume": l.get('volume', 0)
                }
                for l in top_losers
            ]

            summary = {
                "date": str(date_),
                "market": {
                    "total_stocks": total_stocks,
                    "market_change_pct": avg_market_change,
                    "avg_sentiment": avg_sentiment,
                    "total_volume": total_volume,
                    "advancing": market_breadth.get('advancing', 0),
                    "declining": market_breadth.get('declining', 0),
                    "unchanged": market_breadth.get('unchanged', 0),
                },
                "top_gainers": formatted_gainers,
                "top_losers": formatted_losers,
                "sentiment": {
                    "avg_score": avg_sentiment,
                    "positive_pct": positive_pct,
                    "total_articles": article_count,
                },
                "macro": {
                    "cpi": cpi,
                    "usd_vnd": usd_vnd,
                },
                "latest_update": datetime.utcnow().isoformat() if total_stocks > 0 else None,
            }

            return summary

        except Exception as e:
            logger.error(f"Failed to generate dashboard summary: {str(e)}")
            raise

    def get_correlation_analysis(
        self,
        start_date: date,
        end_date: date,
    ) -> dict[str, Any]:
        """
        Get correlation between sentiment, macro indicators, and market movement.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            dict: Correlation analysis
        """
        try:
            sql = f"""
                SELECT 
                    m.data_date,
                    m.symbol,
                    m.price_change_pct,
                    s.avg_sentiment,
                    macro.indicator_value
                FROM fizbert.market_dashboard m
                LEFT JOIN fizbert.sentiment_features s 
                    ON m.partition_date = s.partition_date
                LEFT JOIN fizbert.macro_features macro
                    ON m.partition_date = macro.partition_date
                WHERE m.partition_date >= '{start_date}' 
                    AND m.partition_date <= '{end_date}'
                ORDER BY m.data_date DESC
            """

            logger.info("Fetching correlation analysis data")
            results = self.athena.query(sql)

            return {
                "data": results,
                "period": {"start": str(start_date), "end": str(end_date)},
            }

        except Exception as e:
            logger.error(f"Failed to get correlation analysis: {str(e)}")
            raise

    def _get_market_stats(self, date_: date) -> dict[str, Any]:
        """Get market statistics for a date."""
        try:
            sql = f"""
                SELECT 
                    COUNT(DISTINCT symbol) as total_stocks,
                    AVG(price_change_pct) as avg_market_change,
                    MAX(close) as market_high,
                    MIN(close) as market_low,
                    SUM(volume) as total_volume
                FROM fizbert.market_dashboard
                WHERE partition_date = '{date_}'
            """

            results = self.athena.query(sql)
            return results[0] if results else {}

        except Exception as e:
            logger.error(f"Failed to get market stats: {str(e)}")
            return {}

    def _get_sentiment_stats(self, date_: date) -> dict[str, Any]:
        """Get sentiment statistics for a date."""
        try:
            sql = f"""
                SELECT 
                    avg_sentiment,
                    article_count,
                    positive_pct,
                    negative_pct
                FROM fizbert.sentiment_features
                WHERE partition_date = '{date_}'
            """

            results = self.athena.query(sql)
            return results[0] if results else {}

        except Exception as e:
            logger.error(f"Failed to get sentiment stats: {str(e)}")
            return {}

    def _get_macro_stats(self, date_: date) -> dict[str, Any]:
        """Get macro statistics for a date."""
        try:
            sql = f"""
                SELECT 
                    indicator_name,
                    indicator_value
                FROM fizbert.macro_features
                WHERE partition_date = '{date_}'
                LIMIT 10
            """

            results = self.athena.query(sql)
            return {"indicators": results}

        except Exception as e:
            logger.error(f"Failed to get macro stats: {str(e)}")
            return {"indicators": []}

    def _get_top_movers(self, date_: date, direction: str = 'gainers', limit: int = 5) -> list[dict[str, Any]]:
        """Get top gaining or losing stocks for a date.
        
        Args:
            date_: Date to query
            direction: 'gainers' for top gainers, 'losers' for top losers
            limit: Number of stocks to return
            
        Returns:
            List of stock dictionaries with symbol, price_change_pct, and close
        """
        try:
            order = 'DESC' if direction == 'gainers' else 'ASC'
            
            sql = f"""
                SELECT 
                    symbol,
                    price_change_pct,
                    close,
                    volume
                FROM fizbert.market_dashboard
                WHERE partition_date = '{date_}'
                    AND price_change_pct IS NOT NULL
                ORDER BY price_change_pct {order}
                LIMIT {limit}
            """

            results = self.athena.query(sql)
            
            # Convert to proper types
            for result in results:
                if result.get('price_change_pct'):
                    result['price_change_pct'] = float(result['price_change_pct'])
                if result.get('close'):
                    result['close'] = float(result['close'])
                if result.get('volume'):
                    result['volume'] = int(result['volume']) if result['volume'] else 0
            
            return results

        except Exception as e:
            logger.error(f"Failed to get top {direction}: {str(e)}")
            return []

    def _get_market_breadth(self, date_: date) -> dict[str, Any]:
        """Get market breadth (advancing, declining, unchanged stocks).
        
        Args:
            date_: Date to query
            
        Returns:
            Dictionary with advancing, declining, and unchanged counts
        """
        try:
            sql = f"""
                SELECT 
                    SUM(CASE WHEN price_change_pct > 0 THEN 1 ELSE 0 END) as advancing,
                    SUM(CASE WHEN price_change_pct < 0 THEN 1 ELSE 0 END) as declining,
                    SUM(CASE WHEN price_change_pct = 0 THEN 1 ELSE 0 END) as unchanged
                FROM fizbert.market_dashboard
                WHERE partition_date = '{date_}'
                    AND price_change_pct IS NOT NULL
            """

            results = self.athena.query(sql)
            
            if results and len(results) > 0:
                result = results[0]
                return {
                    "advancing": int(result.get('advancing', 0)) if result.get('advancing') else 0,
                    "declining": int(result.get('declining', 0)) if result.get('declining') else 0,
                    "unchanged": int(result.get('unchanged', 0)) if result.get('unchanged') else 0,
                }
            
            return {"advancing": 0, "declining": 0, "unchanged": 0}

        except Exception as e:
            logger.error(f"Failed to get market breadth: {str(e)}")
            return {"advancing": 0, "declining": 0, "unchanged": 0}
