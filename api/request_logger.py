"""
Request Logging Middleware with Correlation IDs
Provides structured logging for all API requests
"""

import time
import uuid
from functools import wraps
from typing import Callable
from flask import Flask, Request, Response, g, request
import logging

# Set up structured logger
logger = logging.getLogger(__name__)


class RequestLogger:
    """Middleware for logging all requests with correlation IDs."""

    def __init__(self, app: Flask = None):
        """Initialize request logger middleware."""
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize the middleware with a Flask app."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)

    @staticmethod
    def before_request():
        """Log request start and assign correlation ID."""
        # Generate or extract correlation ID
        correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
        g.correlation_id = correlation_id
        g.request_start_time = time.time()

        # Log request details
        logger.info(
            "Request started",
            extra={
                'correlation_id': correlation_id,
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'unknown'),
            }
        )

    @staticmethod
    def after_request(response: Response) -> Response:
        """Log request completion and add correlation ID header."""
        if hasattr(g, 'correlation_id'):
            response.headers['X-Correlation-ID'] = g.correlation_id

        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            logger.info(
                "Request completed",
                extra={
                    'correlation_id': getattr(g, 'correlation_id', 'unknown'),
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration_ms': round(duration * 1000, 2),
                }
            )

        return response

    @staticmethod
    def teardown_request(exception=None):
        """Log any exceptions that occurred during request processing."""
        if exception:
            logger.error(
                "Request failed with exception",
                extra={
                    'correlation_id': getattr(g, 'correlation_id', 'unknown'),
                    'method': request.method,
                    'path': request.path,
                    'exception': str(exception),
                },
                exc_info=True
            )


def with_correlation_id(func: Callable) -> Callable:
    """
    Decorator to ensure correlation ID is available in function context.
    
    Usage:
        @with_correlation_id
        def my_api_endpoint():
            correlation_id = g.correlation_id
            # ... rest of function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(g, 'correlation_id'):
            g.correlation_id = str(uuid.uuid4())
        return func(*args, **kwargs)
    return wrapper


def log_slow_request(threshold_ms: float = 1000):
    """
    Decorator to log slow requests.
    
    Args:
        threshold_ms: Time threshold in milliseconds to consider request slow
        
    Usage:
        @log_slow_request(threshold_ms=500)
        def slow_endpoint():
            # ... endpoint logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000

            if duration_ms > threshold_ms:
                logger.warning(
                    f"Slow request detected: {request.path}",
                    extra={
                        'correlation_id': getattr(g, 'correlation_id', 'unknown'),
                        'method': request.method,
                        'path': request.path,
                        'duration_ms': round(duration_ms, 2),
                        'threshold_ms': threshold_ms,
                    }
                )

            return result
        return wrapper
    return decorator


# Export all
__all__ = [
    'RequestLogger',
    'with_correlation_id',
    'log_slow_request',
]
