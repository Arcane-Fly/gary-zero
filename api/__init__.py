"""
API module for Gary-Zero.

This module contains API endpoints and routers for the Gary-Zero framework.
"""

# Barrel exports for API modules
from api.health import HealthCheckService, create_health_check_response
from api.response_formatter import ApiResponseFormatter, success_response, error_response
from api.request_logger import RequestLogger, with_correlation_id, log_slow_request

__all__ = [
    # Health check
    'HealthCheckService',
    'create_health_check_response',
    # Response formatting
    'ApiResponseFormatter',
    'success_response',
    'error_response',
    # Request logging
    'RequestLogger',
    'with_correlation_id',
    'log_slow_request',
]

