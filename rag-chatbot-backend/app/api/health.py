"""
Health check endpoint for monitoring service availability.
Checks connectivity to all external dependencies.
"""

from datetime import datetime
from fastapi import APIRouter

from app.models.schemas import HealthCheckResponse
from app.database import db_pool
from app.qdrant_client import qdrant_client
from app.gemini_client import gemini_client
from app.middleware.logging import log_info, log_error


router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Check health status of all service dependencies.
    
    Checks:
    - PostgreSQL database connection
    - Qdrant vector database connection
    - Gemini API connectivity
    
    Returns:
        HealthCheckResponse with overall status and individual service status
    """
    log_info("health_check_started")
    
    # Check each service
    services_status = {
        "postgres": False,
        "qdrant": False,
        "gemini": False
    }
    
    # Check PostgreSQL
    try:
        services_status["postgres"] = await db_pool.health_check()
    except Exception as e:
        log_error("postgres_health_check_failed", error=str(e))
    
    # Check Qdrant
    try:
        services_status["qdrant"] = await qdrant_client.health_check()
    except Exception as e:
        log_error("qdrant_health_check_failed", error=str(e))
    
    # Check Gemini API
    try:
        services_status["gemini"] = await gemini_client.health_check()
    except Exception as e:
        log_error("gemini_health_check_failed", error=str(e))
    
    # Determine overall status
    all_healthy = all(services_status.values())
    overall_status = "healthy" if all_healthy else "unhealthy"
    
    log_info(
        "health_check_completed",
        status=overall_status,
        services=services_status
    )
    
    return HealthCheckResponse(
        status=overall_status,
        services=services_status,
        timestamp=datetime.utcnow()
    )
