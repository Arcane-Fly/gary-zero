"""
Standardized Error Response Format
Provides consistent error response structure across the API
"""

from typing import Any, Dict, Optional
import time
import traceback
from flask import jsonify, request


class ApiResponseFormatter:
    """Formats API responses with consistent structure."""

    @staticmethod
    def success(data: Any = None, message: str = None, meta: Dict = None) -> Dict[str, Any]:
        """
        Create a successful API response.
        
        Args:
            data: Response data
            message: Optional success message
            meta: Optional metadata (pagination, etc.)
            
        Returns:
            Standardized success response dictionary
        """
        response = {
            'success': True,
            'timestamp': time.time(),
        }
        
        if data is not None:
            response['data'] = data
            
        if message:
            response['message'] = message
            
        if meta:
            response['meta'] = meta
            
        return response

    @staticmethod
    def error(
        message: str,
        error_code: str = None,
        details: Any = None,
        status_code: int = 400,
        include_trace: bool = False
    ) -> tuple:
        """
        Create an error API response.
        
        Args:
            message: Error message
            error_code: Application-specific error code
            details: Additional error details
            status_code: HTTP status code
            include_trace: Whether to include stack trace (only in dev)
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        response = {
            'success': False,
            'error': message,
            'timestamp': time.time(),
        }
        
        if error_code:
            response['error_code'] = error_code
            
        if details:
            response['details'] = details
            
        if include_trace:
            response['trace'] = traceback.format_exc()
            
        # Add request context for debugging
        if hasattr(request, 'path'):
            response['path'] = request.path
            response['method'] = request.method
            
        return response, status_code

    @staticmethod
    def validation_error(errors: Dict[str, Any]) -> tuple:
        """
        Create a validation error response.
        
        Args:
            errors: Dictionary of field-level validation errors
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        return ApiResponseFormatter.error(
            message='Validation failed',
            error_code='VALIDATION_ERROR',
            details={'validation_errors': errors},
            status_code=422
        )

    @staticmethod
    def not_found(resource: str = None) -> tuple:
        """
        Create a not found error response.
        
        Args:
            resource: Optional resource identifier
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        message = f'{resource} not found' if resource else 'Resource not found'
        return ApiResponseFormatter.error(
            message=message,
            error_code='NOT_FOUND',
            status_code=404
        )

    @staticmethod
    def unauthorized(message: str = 'Unauthorized') -> tuple:
        """
        Create an unauthorized error response.
        
        Args:
            message: Optional custom message
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        return ApiResponseFormatter.error(
            message=message,
            error_code='UNAUTHORIZED',
            status_code=401
        )

    @staticmethod
    def forbidden(message: str = 'Forbidden') -> tuple:
        """
        Create a forbidden error response.
        
        Args:
            message: Optional custom message
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        return ApiResponseFormatter.error(
            message=message,
            error_code='FORBIDDEN',
            status_code=403
        )

    @staticmethod
    def server_error(message: str = 'Internal server error', include_trace: bool = False) -> tuple:
        """
        Create a server error response.
        
        Args:
            message: Error message
            include_trace: Whether to include stack trace
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        return ApiResponseFormatter.error(
            message=message,
            error_code='INTERNAL_ERROR',
            include_trace=include_trace,
            status_code=500
        )

    @staticmethod
    def rate_limit_exceeded(retry_after: int = None) -> tuple:
        """
        Create a rate limit exceeded error response.
        
        Args:
            retry_after: Seconds until rate limit resets
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        details = {'retry_after': retry_after} if retry_after else None
        return ApiResponseFormatter.error(
            message='Rate limit exceeded',
            error_code='RATE_LIMIT_EXCEEDED',
            details=details,
            status_code=429
        )


# Convenience functions
def success_response(data: Any = None, message: str = None, meta: Dict = None):
    """Shorthand for creating success responses."""
    return jsonify(ApiResponseFormatter.success(data, message, meta))


def error_response(
    message: str,
    error_code: str = None,
    details: Any = None,
    status_code: int = 400,
    include_trace: bool = False
):
    """Shorthand for creating error responses."""
    response_data, code = ApiResponseFormatter.error(
        message, error_code, details, status_code, include_trace
    )
    return jsonify(response_data), code


# Export all
__all__ = [
    'ApiResponseFormatter',
    'success_response',
    'error_response',
]
