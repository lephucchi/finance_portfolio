"""
AWS Athena client for querying S3 Gold layer data.
"""

import time
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

from app.core.config import get_logger
from config.settings import settings

logger = get_logger(__name__)


class AthenaClient:
    """
    Client for AWS Athena queries.
    Handles connection, query execution, and result retrieval.
    
    SOLID Principles:
    - Single Responsibility: Only manages Athena interactions
    - Dependency Inversion: Uses boto3 client injected via __init__
    """

    def __init__(self, session: Optional[boto3.Session] = None):
        """
        Initialize Athena client.

        Args:
            session: Boto3 session (optional, creates default if not provided)
        """
        self.session = session or boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

        self.client = self.session.client("athena", region_name=settings.AWS_REGION)
        self.s3_client = self.session.client("s3", region_name=settings.AWS_REGION)
        self.database = settings.ATHENA_DATABASE
        self.output_location = settings.ATHENA_OUTPUT_PATH

    def execute_query(
        self,
        query: str,
        wait_for_completion: bool = True,
        poll_interval: int = 1,
        max_wait_time: int = 300,
    ) -> str:
        """
        Execute Athena query.

        Args:
            query: SQL query string
            wait_for_completion: Whether to wait for query completion
            poll_interval: Polling interval in seconds
            max_wait_time: Maximum wait time in seconds

        Returns:
            str: Query execution ID

        Raises:
            RuntimeError: If query execution fails or times out
        """
        try:
            logger.info(f"Executing Athena query: {query[:100]}...")

            response = self.client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={"Database": self.database},
                ResultConfiguration={"OutputLocation": self.output_location},
            )

            query_id = response["QueryExecutionId"]
            logger.info(f"Query started with ID: {query_id}")

            if wait_for_completion:
                self._wait_for_query_completion(
                    query_id, poll_interval, max_wait_time
                )

            return query_id

        except ClientError as e:
            logger.error(f"Athena query execution failed: {str(e)}")
            raise RuntimeError(f"Query execution failed: {str(e)}")

    def get_query_results(
        self, query_id: str, max_results: int = 1000
    ) -> list[dict[str, Any]]:
        """
        Get query results.

        Args:
            query_id: Query execution ID
            max_results: Maximum number of results to return

        Returns:
            list: Query results as list of dictionaries

        Raises:
            RuntimeError: If results cannot be retrieved
        """
        try:
            logger.info(f"Fetching results for query: {query_id}")

            response = self.client.get_query_results(
                QueryExecutionId=query_id, MaxResults=max_results
            )

            # Extract column names from first row (header)
            columns = [col["Name"] for col in response["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]]

            # Convert rows to dictionaries
            results = []
            for row in response["ResultSet"]["Rows"][1:]:  # Skip header row
                result_dict = {
                    columns[i]: row["Data"][i].get("VarCharValue", None)
                    for i in range(len(columns))
                }
                results.append(result_dict)

            logger.info(f"Retrieved {len(results)} results from query: {query_id}")
            return results

        except ClientError as e:
            logger.error(f"Failed to get query results: {str(e)}")
            raise RuntimeError(f"Failed to retrieve results: {str(e)}")

    def get_query_status(self, query_id: str) -> str:
        """
        Get query execution status.

        Args:
            query_id: Query execution ID

        Returns:
            str: Query status (QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELLED)
        """
        try:
            response = self.client.get_query_execution(QueryExecutionId=query_id)
            status = response["QueryExecution"]["Status"]["State"]
            return status

        except ClientError as e:
            logger.error(f"Failed to get query status: {str(e)}")
            raise RuntimeError(f"Failed to get status: {str(e)}")

    def _wait_for_query_completion(
        self,
        query_id: str,
        poll_interval: int = 1,
        max_wait_time: int = 300,
    ) -> None:
        """
        Wait for query to complete.

        Args:
            query_id: Query execution ID
            poll_interval: Polling interval in seconds
            max_wait_time: Maximum wait time in seconds

        Raises:
            TimeoutError: If query doesn't complete within max_wait_time
            RuntimeError: If query fails
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            if elapsed > max_wait_time:
                logger.error(f"Query {query_id} timed out after {elapsed}s")
                raise TimeoutError(f"Query timed out after {max_wait_time}s")

            status = self.get_query_status(query_id)

            if status == "SUCCEEDED":
                logger.info(f"Query {query_id} completed successfully")
                return

            elif status == "FAILED":
                response = self.client.get_query_execution(QueryExecutionId=query_id)
                reason = response["QueryExecution"]["Status"].get("StateChangeReason", "Unknown")
                logger.error(f"Query {query_id} failed: {reason}")
                raise RuntimeError(f"Query failed: {reason}")

            elif status == "CANCELLED":
                logger.warning(f"Query {query_id} was cancelled")
                raise RuntimeError("Query was cancelled")

            time.sleep(poll_interval)

    def query(self, sql: str, max_results: int = 1000) -> list[dict[str, Any]]:
        """
        Execute query and return results (convenience method).

        Args:
            sql: SQL query string
            max_results: Maximum number of results

        Returns:
            list: Query results
        """
        query_id = self.execute_query(sql)
        return self.get_query_results(query_id, max_results)
