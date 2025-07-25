from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Health check endpoint for Kubernetes liveness and readiness probes
    """
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    # Check cache connection
    try:
        cache.set("health_check", "ok", 1)
        if cache.get("health_check") == "ok":
            health_status["services"]["cache"] = "healthy"
        else:
            health_status["services"]["cache"] = "unhealthy"
            health_status["status"] = "unhealthy"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        health_status["services"]["cache"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return JsonResponse(health_status, status=status_code)