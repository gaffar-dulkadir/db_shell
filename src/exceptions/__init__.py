"""
Custom Exceptions for Chat Marketplace Service
"""

from typing import Optional, Dict, Any

class ChatMarketplaceException(Exception):
    """Base exception for Chat Marketplace Service"""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(ChatMarketplaceException):
    """Validation error exception"""
    pass

class NotFoundError(ChatMarketplaceException):
    """Resource not found exception"""
    pass

class DuplicateError(ChatMarketplaceException):
    """Duplicate resource exception"""
    pass

class AuthenticationError(ChatMarketplaceException):
    """Authentication failed exception"""
    pass

class AuthorizationError(ChatMarketplaceException):
    """Authorization failed exception"""
    pass

class DatabaseError(ChatMarketplaceException):
    """Database operation error exception"""
    pass

class ServiceUnavailableError(ChatMarketplaceException):
    """Service unavailable exception"""
    pass

class BusinessLogicError(ChatMarketplaceException):
    """Business logic violation exception"""
    pass

class ConfigurationError(ChatMarketplaceException):
    """Configuration error exception"""
    pass

class ExternalServiceError(ChatMarketplaceException):
    """External service error exception"""
    pass

# User-specific exceptions
class UserNotFoundError(NotFoundError):
    """User not found exception"""
    
    def __init__(self, user_id: str):
        super().__init__(f"User not found: {user_id}", "USER_NOT_FOUND", {"user_id": user_id})

class UserAlreadyExistsError(DuplicateError):
    """User already exists exception"""
    
    def __init__(self, email: str):
        super().__init__(f"User already exists: {email}", "USER_ALREADY_EXISTS", {"email": email})

class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials exception"""
    
    def __init__(self):
        super().__init__("Invalid email or password", "INVALID_CREDENTIALS")

class UserInactiveError(AuthenticationError):
    """User account inactive exception"""
    
    def __init__(self, user_id: str):
        super().__init__(f"User account is inactive: {user_id}", "USER_INACTIVE", {"user_id": user_id})

# Conversation-specific exceptions
class ConversationNotFoundError(NotFoundError):
    """Conversation not found exception"""
    
    def __init__(self, conversation_id: str):
        super().__init__(f"Conversation not found: {conversation_id}", "CONVERSATION_NOT_FOUND", {"conversation_id": conversation_id})

class ConversationAccessDeniedError(AuthorizationError):
    """Conversation access denied exception"""
    
    def __init__(self, conversation_id: str, user_id: str):
        super().__init__(f"Access denied to conversation: {conversation_id}", "CONVERSATION_ACCESS_DENIED", {"conversation_id": conversation_id, "user_id": user_id})

# Message-specific exceptions
class MessageNotFoundError(NotFoundError):
    """Message not found exception"""
    
    def __init__(self, message_id: str):
        super().__init__(f"Message not found: {message_id}", "MESSAGE_NOT_FOUND", {"message_id": message_id})

class MessageAccessDeniedError(AuthorizationError):
    """Message access denied exception"""
    
    def __init__(self, message_id: str, user_id: str):
        super().__init__(f"Access denied to message: {message_id}", "MESSAGE_ACCESS_DENIED", {"message_id": message_id, "user_id": user_id})

# Bot-specific exceptions
class BotNotFoundError(NotFoundError):
    """Bot not found exception"""
    
    def __init__(self, bot_id: str):
        super().__init__(f"Bot not found: {bot_id}", "BOT_NOT_FOUND", {"bot_id": bot_id})

class BotAlreadyExistsError(DuplicateError):
    """Bot already exists exception"""
    
    def __init__(self, bot_name: str):
        super().__init__(f"Bot already exists: {bot_name}", "BOT_ALREADY_EXISTS", {"bot_name": bot_name})

class CategoryNotFoundError(NotFoundError):
    """Category not found exception"""
    
    def __init__(self, category_id: str):
        super().__init__(f"Category not found: {category_id}", "CATEGORY_NOT_FOUND", {"category_id": category_id})

class CategoryAlreadyExistsError(DuplicateError):
    """Category already exists exception"""
    
    def __init__(self, category_name: str):
        super().__init__(f"Category already exists: {category_name}", "CATEGORY_ALREADY_EXISTS", {"category_name": category_name})

# Database-specific exceptions
class PostgreSQLConnectionError(DatabaseError):
    """PostgreSQL connection error"""
    
    def __init__(self, details: str):
        super().__init__(f"PostgreSQL connection failed: {details}", "POSTGRES_CONNECTION_ERROR", {"details": details})

class TransactionError(DatabaseError):
    """Database transaction error"""
    
    def __init__(self, operation: str, details: str):
        super().__init__(f"Transaction failed during {operation}: {details}", "TRANSACTION_ERROR", {"operation": operation, "details": details})

# Rate limiting exceptions
class RateLimitExceededError(ChatMarketplaceException):
    """Rate limit exceeded exception"""
    
    def __init__(self, limit: int, window: int):
        super().__init__(f"Rate limit exceeded: {limit} requests per {window} seconds", "RATE_LIMIT_EXCEEDED", {"limit": limit, "window": window})

# File handling exceptions
class FileUploadError(ChatMarketplaceException):
    """File upload error exception"""
    
    def __init__(self, filename: str, reason: str):
        super().__init__(f"File upload failed for {filename}: {reason}", "FILE_UPLOAD_ERROR", {"filename": filename, "reason": reason})

class FileSizeExceededError(ValidationError):
    """File size exceeded exception"""
    
    def __init__(self, filename: str, size: int, max_size: int):
        super().__init__(f"File size exceeded for {filename}: {size} bytes (max: {max_size})", "FILE_SIZE_EXCEEDED", {"filename": filename, "size": size, "max_size": max_size})

__all__ = [
    # Base exceptions
    "ChatMarketplaceException",
    "ValidationError",
    "NotFoundError",
    "DuplicateError",
    "AuthenticationError",
    "AuthorizationError",
    "DatabaseError",
    "ServiceUnavailableError",
    "BusinessLogicError",
    "ConfigurationError",
    "ExternalServiceError",
    # User exceptions
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "InvalidCredentialsError",
    "UserInactiveError",
    # Conversation exceptions
    "ConversationNotFoundError",
    "ConversationAccessDeniedError",
    # Message exceptions
    "MessageNotFoundError",
    "MessageAccessDeniedError",
    # Bot exceptions
    "BotNotFoundError",
    "BotAlreadyExistsError",
    "CategoryNotFoundError",
    "CategoryAlreadyExistsError",
    # Database exceptions
    "PostgreSQLConnectionError",
    "TransactionError",
    # Other exceptions
    "RateLimitExceededError",
    "FileUploadError",
    "FileSizeExceededError"
]