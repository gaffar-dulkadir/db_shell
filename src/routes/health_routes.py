"""
Health Routes for Chat Marketplace Service
Basic health check endpoints
"""

import logging
from fastapi import APIRouter, Depends
from datalayer.database import health_check

logger = logging.getLogger(__name__)

# Router configuration
router = APIRouter(
    tags=["Health"],
    responses={503: {"description": "Service unavailable"}}
)

@router.get(
    "/health",
    summary="Health check",
    description="Check the health status of the Chat Marketplace service and PostgreSQL database"
)
async def health_check_endpoint():
    """Perform health check"""
    logger.info("🚀 API: Health check requested")
    
    try:
        health = await health_check()
        logger.info(f"✅ API: Health check completed: {health.get('status', 'unknown')}")
        
        if health.get("status") == "healthy":
            return {
                "status": "healthy",
                "service": "Chat Marketplace Service",
                "version": "2.0.0",
                "database": health
            }
        else:
            return {
                "status": "unhealthy", 
                "service": "Chat Marketplace Service",
                "version": "2.0.0",
                "database": health
            }
        
    except Exception as e:
        logger.error(f"❌ API: Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "Chat Marketplace Service", 
            "version": "2.0.0",
            "error": str(e)
        }

__all__ = ["router"]