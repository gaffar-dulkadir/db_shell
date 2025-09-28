# Chat Marketplace routes
from .health_routes import router as health_router
from .user_routes import router as user_router
from .profile_routes import router as profile_router, search_router as profile_search_router
from .settings_routes import router as settings_router
from .conversation_routes import router as conversation_router
from .message_routes import router as message_router, documents_router, memory_router
from .bot_routes import categories_router, bots_router

__all__ = [
    # Health routes
    "health_router",
    # Auth & User routes
    "user_router",
    "profile_router",
    "profile_search_router",
    "settings_router",
    # Chat routes
    "conversation_router",
    "message_router",
    "documents_router",
    "memory_router",
    # Marketplace routes
    "categories_router",
    "bots_router"
]