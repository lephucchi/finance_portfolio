"""
Sentiment analysis service - handles news sentiment queries.
"""

import hashlib
from datetime import date
from typing import Any, Optional

from app.core.config import get_logger
from app.db import AthenaClient, SupabaseClient

logger = get_logger(__name__)


class SentimentService:
    """
    Sentiment analysis service.
    Manages news sentiment data and analysis.
    
    SOLID Principles:
    - Single Responsibility: Only handles sentiment operations
    - Dependency Inversion: Takes database clients as dependencies
    """

    def __init__(self, athena_client: AthenaClient, supabase_client: SupabaseClient):
        """
        Initialize sentiment service.

        Args:
            athena_client: Athena client instance
            supabase_client: Supabase client instance
        """
        self.athena = athena_client
        self.supabase = supabase_client

    def get_sentiment_summary(
        self,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        """
        Get daily sentiment summary.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            list: Daily sentiment data
        """
        try:
            sql = f"""
                SELECT 
                    data_date,
                    article_count,
                    avg_sentiment,
                    positive_pct,
                    negative_pct
                FROM fizbert.sentiment_features
                WHERE partition_date BETWEEN '{start_date}' AND '{end_date}'
                ORDER BY data_date DESC
            """

            # Check cache
            query_hash = self._hash_query(sql)
            cached = self.supabase.get_cached_result(query_hash)
            if cached:
                logger.info("Returning cached sentiment summary")
                return cached["result"]

            logger.info(f"Fetching sentiment summary from {start_date} to {end_date}")
            results = self.athena.query(sql)

            # Cache results
            self.supabase.cache_result(query_hash, sql, results)

            return results

        except Exception as e:
            logger.error(f"Failed to get sentiment summary: {str(e)}")
            raise

    def get_news_articles(
        self,
        start_date: date,
        end_date: date,
        sentiment_filter: Optional[str] = None,  # positive, negative, neutral
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get news articles with sentiment.

        Args:
            start_date: Start date
            end_date: End date
            sentiment_filter: Filter by sentiment type
            limit: Maximum number of articles

        Returns:
            list: News articles
        """
        try:
            sentiment_clause = ""
            if sentiment_filter == "positive":
                sentiment_clause = "AND sentiment_score > 0.3"
            elif sentiment_filter == "negative":
                sentiment_clause = "AND sentiment_score < -0.3"

            sql = f"""
                SELECT 
                    id,
                    data_date,
                    title,
                    source,
                    sentiment_score,
                    link
                FROM fizbert.news
                WHERE partition_date BETWEEN '{start_date}' AND '{end_date}'
                    {sentiment_clause}
                ORDER BY data_date DESC, sentiment_score DESC
                LIMIT {limit}
            """

            logger.info("Fetching news articles")
            return self.athena.query(sql)

        except Exception as e:
            logger.error(f"Failed to get news articles: {str(e)}")
            raise

    def get_sentiment_trend(
        self,
        start_date: date,
        end_date: date,
        interval: str = "daily",  # daily, weekly, monthly
    ) -> list[dict[str, Any]]:
        """
        Get sentiment trend over time.

        Args:
            start_date: Start date
            end_date: End date
            interval: Time interval for aggregation

        Returns:
            list: Sentiment trend data
        """
        try:
            # Build date grouping based on interval
            if interval == "weekly":
                date_group = "DATE_TRUNC('week', data_date)"
            elif interval == "monthly":
                date_group = "DATE_TRUNC('month', data_date)"
            else:
                date_group = "data_date"

            sql = f"""
                SELECT 
                    {date_group} as period,
                    AVG(avg_sentiment) as avg_sentiment,
                    SUM(article_count) as article_count
                FROM fizbert.sentiment_features
                WHERE partition_date BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY {date_group}
                ORDER BY period DESC
            """

            logger.info(f"Fetching sentiment trend ({interval})")
            return self.athena.query(sql)

        except Exception as e:
            logger.error(f"Failed to get sentiment trend: {str(e)}")
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
