"""
Supabase client for query logging, caching, and user management.
"""

from datetime import datetime
from typing import Any, Optional

from supabase import create_client

from app.core.config import get_logger
from config.settings import settings

logger = get_logger(__name__)


class SupabaseClient:
    """
    Client for Supabase interactions.
    Handles query logging, caching, and metadata storage.
    
    SOLID Principles:
    - Single Responsibility: Only manages Supabase interactions
    - Dependency Inversion: Uses Supabase client initialized externally
    """

    def __init__(self):
        """Initialize Supabase client."""
        try:
            # Try to initialize Supabase client
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            self.enabled = True
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.warning(f"Supabase client initialization failed: {str(e)}")
            logger.warning("Running without Supabase caching - all operations will be skipped")
            self.client = None
            self.enabled = False

    def log_query(
        self,
        user_id: str,
        query: str,
        execution_time_ms: float,
        rows_returned: int,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Log query execution to Supabase.

        Args:
            user_id: User ID
            query: SQL query executed
            execution_time_ms: Execution time in milliseconds
            rows_returned: Number of rows returned
            status: Query status (success, failed, timeout)
            error_message: Error message if status is not success

        Returns:
            dict: Inserted record
        """
        if not self.enabled:
            logger.debug("Supabase logging skipped - client not initialized")
            return {}
            
        try:
            data = {
                "user_id": user_id,
                "query": query,
                "execution_time_ms": execution_time_ms,
                "rows_returned": rows_returned,
                "status": status,
                "error_message": error_message,
                "created_at": datetime.utcnow().isoformat(),
            }

            response = self.client.table("query_logs").insert(data).execute()
            logger.info(f"Query logged for user: {user_id}")
            return response.data[0] if response.data else data

        except Exception as e:
            logger.error(f"Failed to log query: {str(e)}")
            return {}

    def get_cached_result(self, query_hash: str) -> Optional[dict[str, Any]]:
        """
        Get cached query result.

        Args:
            query_hash: Hash of the query

        Returns:
            dict: Cached result or None if not found/expired
        """
        if not self.enabled:
            logger.debug("Supabase caching skipped - client not initialized")
            return None
            
        try:
            response = (
                self.client.table("query_cache")
                .select("*")
                .eq("query_hash", query_hash)
                .execute()
            )

            if response.data:
                record = response.data[0]
                # Check if cache expired
                if self._is_cache_valid(record["created_at"]):
                    logger.info(f"Cache hit for query: {query_hash}")
                    return record
                else:
                    logger.info(f"Cache expired for query: {query_hash}")

            return None

        except Exception as e:
            logger.error(f"Failed to get cached result: {str(e)}")
            return None

    def cache_result(
        self,
        query_hash: str,
        query: str,
        result: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Cache query result.

        Args:
            query_hash: Hash of the query
            query: SQL query
            result: Query result to cache

        Returns:
            dict: Cached record
        """
        if not self.enabled:
            logger.debug("Supabase caching skipped - client not initialized")
            return {}
            
        try:
            data = {
                "query_hash": query_hash,
                "query": query,
                "result": result,
                "created_at": datetime.utcnow().isoformat(),
            }

            response = self.client.table("query_cache").insert(data).execute()
            logger.info(f"Result cached for query: {query_hash}")
            return response.data[0] if response.data else data

        except Exception as e:
            logger.error(f"Failed to cache result: {str(e)}")
            return {}

    def get_user_by_email(self, email: str) -> Optional[dict[str, Any]]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            dict: User record or None
        """
        if not self.enabled:
            logger.debug("Supabase user lookup skipped - client not initialized")
            return None
            
        try:
            response = (
                self.client.table("users")
                .select("*")
                .eq("email", email)
                .execute()
            )

            return response.data[0] if response.data else None

        except Exception as e:
            logger.error(f"Failed to get user: {str(e)}")
            return None

    def _is_cache_valid(self, created_at: str) -> bool:
        """
        Check if cache is still valid.

        Args:
            created_at: Cache creation timestamp

        Returns:
            bool: True if cache is valid
        """
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        elapsed = (datetime.utcnow() - created).total_seconds()
        return elapsed < settings.CACHE_TTL_SECONDS
