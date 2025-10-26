"""Request/Response middleware for logging and tracking."""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all HTTP requests and responses.
    Tracks request duration and logs details.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            Response: HTTP response
        """
        # Record start time
        start_time = time.time()

        # Get request details
        request_id = request.headers.get("x-request-id", "unknown")
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"

        logger.info(
            f"[{request_id}] {method} {path} from {client_host}",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "client": client_host,
            },
        )

        try:
            # Call next middleware/handler
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                f"[{request_id}] {method} {path} - {response.status_code} ({duration:.2f}s)",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration_ms": duration * 1000,
                },
            )

            # Add custom headers
            response.headers["x-request-id"] = request_id
            response.headers["x-process-time"] = str(duration)

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"[{request_id}] {method} {path} - Error: {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "error": str(e),
                    "duration_ms": duration * 1000,
                },
            )
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling and formatting errors."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Handle exceptions and format error responses.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            Response: HTTP response
        """
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}")
            raise
