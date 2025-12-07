"""
Request tracing and structured logging middleware.
Uses structlog for JSON-formatted logging with request IDs.
"""

import uuid
import time
import structlog
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings


# Map log level names to logging module constants
import logging
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        LOG_LEVEL_MAP.get(settings.log_level, logging.INFO)
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request tracing and structured logging.
    
    Features:
    - Generates unique request_id for each request
    - Logs request start, end, and duration
    - Adds request_id to all log entries
    - Includes request_id in error responses
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with tracing and logging.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler
        
        Returns:
            HTTP response with added headers
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Bind request_id to logging context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None
        )
        
        # Log request start
        start_time = time.time()
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params)
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log request completion
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2)
            )
            
            # Add request_id to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
        
        except Exception as exc:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(
                "request_failed",
                error=str(exc),
                error_type=type(exc).__name__,
                duration_ms=round(duration_ms, 2)
            )
            
            # Re-raise exception to be handled by exception handlers
            raise


def get_request_id(request: Request) -> str:
    """
    Get the request ID from the request state.
    
    Args:
        request: FastAPI request object
    
    Returns:
        Request ID string
    """
    return getattr(request.state, "request_id", "unknown")


def log_info(message: str, **kwargs):
    """Log info level message with context."""
    logger.info(message, **kwargs)


def log_warning(message: str, **kwargs):
    """Log warning level message with context."""
    logger.warning(message, **kwargs)


def log_error(message: str, **kwargs):
    """Log error level message with context."""
    logger.error(message, **kwargs)


def log_debug(message: str, **kwargs):
    """Log debug level message with context."""
    logger.debug(message, **kwargs)
