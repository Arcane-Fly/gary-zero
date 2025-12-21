"""
API Health Check Module
Provides comprehensive health check endpoints for monitoring and diagnostics
"""

import os
import time
from typing import Any, Dict

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class HealthCheckService:
    """Service for performing health checks on various system components."""

    def __init__(self, app=None):
        """Initialize health check service with optional Flask app."""
        self.app = app
        self.startup_time = time.time()
        if app:
            self.startup_time = getattr(app, '_startup_time', time.time())

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-level metrics."""
        metrics = {
            'timestamp': time.time(),
            'uptime_seconds': time.time() - self.startup_time,
        }

        if PSUTIL_AVAILABLE:
            try:
                metrics['memory'] = {
                    'percent': psutil.virtual_memory().percent,
                    'available_mb': psutil.virtual_memory().available / (1024 * 1024),
                    'total_mb': psutil.virtual_memory().total / (1024 * 1024),
                }
                metrics['cpu'] = {
                    'percent': psutil.cpu_percent(interval=0.1),
                    'count': psutil.cpu_count(),
                }
                metrics['disk'] = {
                    'percent': psutil.disk_usage('/').percent,
                    'free_gb': psutil.disk_usage('/').free / (1024 * 1024 * 1024),
                }
            except Exception as e:
                metrics['metrics_error'] = str(e)

        return metrics

    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment configuration information."""
        return {
            'node_env': os.environ.get('NODE_ENV', 'development'),
            'python_version': os.environ.get('PYTHON_VERSION', 'unknown'),
            'server': 'gunicorn' if 'gunicorn' in os.environ.get('SERVER_SOFTWARE', '') else 'development',
            'railway_environment': os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
            'production_mode': os.environ.get('NODE_ENV') == 'production',
        }

    def get_dependencies_status(self) -> Dict[str, Any]:
        """Check status of critical dependencies."""
        dependencies = {
            'psutil': PSUTIL_AVAILABLE,
        }

        # Check Flask
        try:
            import flask
            dependencies['flask'] = {
                'available': True,
                'version': flask.__version__,
            }
        except ImportError:
            dependencies['flask'] = {
                'available': False,
            }

        # Check other critical dependencies
        critical_modules = [
            'werkzeug',
            'langchain',
            'openai',
        ]

        for module_name in critical_modules:
            try:
                module = __import__(module_name)
                dependencies[module_name] = {
                    'available': True,
                    'version': getattr(module, '__version__', 'unknown'),
                }
            except ImportError:
                dependencies[module_name] = {
                    'available': False,
                }

        return dependencies

    def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive health check including all subsystems."""
        return {
            'status': 'healthy',
            'version': '1.0.0',
            'service': 'gary-zero',
            'system': self.get_system_metrics(),
            'environment': self.get_environment_info(),
            'dependencies': self.get_dependencies_status(),
        }

    def get_basic_health(self) -> Dict[str, Any]:
        """Get basic health check (minimal overhead)."""
        return {
            'status': 'healthy',
            'timestamp': time.time(),
            'uptime_seconds': time.time() - self.startup_time,
        }


def create_health_check_response(detailed: bool = False, service: 'HealthCheckService' = None) -> Dict[str, Any]:
    """
    Create a standardized health check response.
    
    Args:
        detailed: If True, include comprehensive system metrics
        service: Optional HealthCheckService instance
        
    Returns:
        Health check response dictionary
    """
    if service is None:
        service = HealthCheckService()

    try:
        if detailed:
            return service.get_comprehensive_health()
        else:
            return service.get_basic_health()
    except Exception as e:
        return {
            'status': 'degraded',
            'error': str(e),
            'timestamp': time.time(),
        }


# Export convenience functions
__all__ = ['HealthCheckService', 'create_health_check_response']
