from datetime import datetime, timezone
import logging
import os
import asyncio
from fastapi.responses import JSONResponse

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from routes import (
    health_router, user_router, profile_router, profile_search_router,
    settings_router, conversation_router, message_router, documents_router,
    memory_router, categories_router, bots_router
)
from logger import setup_logger
from exceptions import (
    ChatMarketplaceException, ValidationError, NotFoundError, DuplicateError,
    AuthenticationError, AuthorizationError, DatabaseError, ServiceUnavailableError,
    RateLimitExceededError
)


setup_logger()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chat Marketplace Service",
    description="A production-ready REST API for WhatsApp-like chat marketplace with comprehensive user, conversation, message, and bot management operations",
    version="2.0.0",
    contact={
        "name": "Chat Marketplace API Support Team",
        "url": "https://yourcompany.com/contact",
        "email": "support@yourcompany.com",
    },
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False,  # Disable automatic redirect for trailing slashes
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik origin'ler belirtilmeli
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

# Static files mounting (hata kontrolü ile)
static_dir = "static" if os.path.exists("static") else "src/static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Static files mounted from: {static_dir}")
else:
    logger.warning(f"Static directory not found: {static_dir}")

# Include routers
try:
    app.include_router(health_router)
    logger.info("Health routes included successfully")
except Exception as e:
    logger.error(f"Failed to include health routes: {e}")

try:
    app.include_router(user_router)
    logger.info("User routes included successfully")
except Exception as e:
    logger.error(f"Failed to include user routes: {e}")

try:
    app.include_router(profile_router)
    logger.info("Profile routes included successfully")
except Exception as e:
    logger.error(f"Failed to include profile routes: {e}")

try:
    app.include_router(profile_search_router)
    logger.info("Profile search routes included successfully")
except Exception as e:
    logger.error(f"Failed to include profile search routes: {e}")

try:
    app.include_router(settings_router)
    logger.info("Settings routes included successfully")
except Exception as e:
    logger.error(f"Failed to include settings routes: {e}")

try:
    app.include_router(conversation_router)
    logger.info("Conversation routes included successfully")
except Exception as e:
    logger.error(f"Failed to include conversation routes: {e}")

try:
    app.include_router(message_router)
    logger.info("Message routes included successfully")
except Exception as e:
    logger.error(f"Failed to include message routes: {e}")

try:
    app.include_router(documents_router)
    logger.info("Documents routes included successfully")
except Exception as e:
    logger.error(f"Failed to include documents routes: {e}")

try:
    app.include_router(memory_router)
    logger.info("Memory routes included successfully")
except Exception as e:
    logger.error(f"Failed to include memory routes: {e}")

try:
    app.include_router(categories_router)
    logger.info("Categories routes included successfully")
except Exception as e:
    logger.error(f"Failed to include categories routes: {e}")

try:
    app.include_router(bots_router)
    logger.info("Bots routes included successfully")
except Exception as e:
    logger.error(f"Failed to include bots routes: {e}")

# Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    logger.warning(f"Validation error: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )

@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request, exc: NotFoundError):
    logger.warning(f"Not found error: {exc.message}")
    return JSONResponse(
        status_code=404,
        content={
            "detail": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )

@app.exception_handler(DuplicateError)
async def duplicate_exception_handler(request, exc: DuplicateError):
    logger.warning(f"Duplicate error: {exc.message}")
    return JSONResponse(
        status_code=409,
        content={
            "detail": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )

@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request, exc: AuthenticationError):
    logger.warning(f"Authentication error: {exc.message}")
    return JSONResponse(
        status_code=401,
        content={
            "detail": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )

@app.exception_handler(AuthorizationError)
async def authorization_exception_handler(request, exc: AuthorizationError):
    logger.warning(f"Authorization error: {exc.message}")
    return JSONResponse(
        status_code=403,
        content={
            "detail": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )

@app.exception_handler(DatabaseError)
async def database_exception_handler(request, exc: DatabaseError):
    logger.error(f"Database error: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Database operation failed",
            "code": exc.code,
            "details": {"message": "Please try again later"}
        }
    )

@app.exception_handler(ServiceUnavailableError)
async def service_unavailable_exception_handler(request, exc: ServiceUnavailableError):
    logger.error(f"Service unavailable: {exc.message}")
    return JSONResponse(
        status_code=503,
        content={
            "detail": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )

@app.exception_handler(RateLimitExceededError)
async def rate_limit_exception_handler(request, exc: RateLimitExceededError):
    logger.warning(f"Rate limit exceeded: {exc.message}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )

@app.exception_handler(ChatMarketplaceException)
async def chat_marketplace_exception_handler(request, exc: ChatMarketplaceException):
    logger.error(f"Chat marketplace exception: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )

@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    logger.warning(f"Value error: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "code": "VALIDATION_ERROR"
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "code": "INTERNAL_ERROR",
            "error": str(exc) if os.getenv("APP_ENV") == "development" else "An unexpected error occurred"
        }
    )
# Helper function for root endpoint
async def _root_impl():
    """Implementation for root endpoint"""
    return {
        "service": "Chat Marketplace Service",
        "version": "2.0.0",
        "description": "REST API for WhatsApp-like chat marketplace with comprehensive user, conversation, message, and bot management",
        "docs_url": "/docs",
        "health_url": "/health",
        "trailing_slash_support": "Both with and without trailing slashes are supported",
        "endpoints": {
            "users": "/users",
            "user_profiles": "/users/{user_id}/profile",
            "user_settings": "/users/{user_id}/settings",
            "conversations": "/users/{user_id}/conversations",
            "messages": "/users/{user_id}/conversations/{conversation_id}/messages",
            "documents": "/users/{user_id}/conversations/{conversation_id}/documents",
            "memory": "/users/{user_id}/conversations/{conversation_id}/memory-history",
            "bot_categories": "/marketplace/bot-categories",
            "bots": "/marketplace/bots",
            "admin": "/admin/*"
        }
    }

# Root endpoints - both with and without trailing slash
@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Get basic API information"
)
async def root():
    """API root endpoint (without trailing slash)"""
    return await _root_impl()

# Note: FastAPI doesn't support empty string paths well,
# so trailing slash support is handled by redirect_slashes=False setting

if __name__ == "__main__":
    print("🚀 Starting Chat Marketplace Service...")
    print("📝 Logs will appear in both console and app.log file")
    print("🔧 Debug: Current working directory:", __import__("os").getcwd())
    print("🔧 Debug: __file__:", __file__)
    
    # Check if running in production
    environment = os.getenv("APP_ENV", "development").lower()
    is_production = environment == "production"
    
    print(f"🔧 Environment: {environment}")
    print("=" * 50)

    import uvicorn

    # Production configuration
    if is_production:
        print("🚀 Running in PRODUCTION mode")
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=int(os.getenv("APP_PORT", "8080")),
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
            reload=False,
            access_log=True,
            workers=int(os.getenv("WORKERS", "1")),
        )
    else:
        print("🚀 Running in DEVELOPMENT mode")
        uvicorn.run(
            "app:app",  # Import string for reload functionality
            host="0.0.0.0",
            port=int(os.getenv("APP_PORT", "8080")),
            log_level="info",
            reload=True,
            access_log=True,
        )

