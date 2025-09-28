"""
Chat DTOs for Chat Marketplace Service
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from .base_dto import BaseDto

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    SYSTEM = "system"

# Conversation DTOs
class ConversationCreateDto(BaseDto):
    bot_id: Optional[str] = Field(None, description="Bot ID for bot conversations")
    title: str = Field(..., min_length=1, max_length=200, description="Conversation title")
    description: Optional[str] = Field(None, max_length=1000, description="Conversation description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ConversationUpdateDto(BaseDto):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[ConversationStatus] = None
    metadata: Optional[Dict[str, Any]] = None

class ConversationResponseDto(BaseDto):
    conversation_id: str
    user_id: str
    bot_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: ConversationStatus
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    message_count: Optional[int] = 0

class ConversationWithMessagesDto(ConversationResponseDto):
    messages: List["MessageResponseDto"] = []
    bot: Optional["BotResponseDto"] = None

class ConversationListResponseDto(BaseDto):
    conversations: List[ConversationResponseDto]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool

# Message DTOs
class MessageCreateDto(BaseDto):
    sender_type: str = Field(..., description="Sender type: 'user' or 'bot'")
    sender_id: str = Field(..., description="Sender ID (user_id or bot_id)")
    message_type: MessageType = Field(default=MessageType.TEXT)
    content: str = Field(..., min_length=1, description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @validator('sender_type')
    def validate_sender_type(cls, v):
        if v not in ['user', 'bot']:
            raise ValueError('sender_type must be either "user" or "bot"')
        return v

class MessageUpdateDto(BaseDto):
    content: Optional[str] = Field(None, min_length=1)
    metadata: Optional[Dict[str, Any]] = None
    is_edited: Optional[bool] = None

class MessageResponseDto(BaseDto):
    message_id: str
    conversation_id: str
    parent_message_id: Optional[str] = None
    sender_type: str
    sender_id: str
    message_type: MessageType
    content: str
    metadata: Optional[Dict[str, Any]] = None
    is_edited: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

class MessageWithDocumentsDto(MessageResponseDto):
    documents: List["DocumentResponseDto"] = []
    parent_message: Optional["MessageResponseDto"] = None

class MessageListResponseDto(BaseDto):
    messages: List[MessageResponseDto]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool

# Document DTOs
class DocumentCreateDto(BaseDto):
    file_name: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., min_length=1, max_length=50)
    file_size: int = Field(..., gt=0, description="File size in bytes")
    file_url: str = Field(..., min_length=1, max_length=500)
    mime_type: str = Field(..., min_length=1, max_length=100)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class DocumentResponseDto(BaseDto):
    document_id: str
    message_id: str
    file_name: str
    file_type: str
    file_size: int
    file_url: str
    mime_type: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

class DocumentListResponseDto(BaseDto):
    documents: List[DocumentResponseDto]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool

# Memory History DTOs
class MemoryHistoryCreateDto(BaseDto):
    memory_key: str = Field(..., min_length=1, max_length=100)
    memory_value: str = Field(..., min_length=1, description="Memory content")
    memory_type: str = Field(default='context', max_length=50)
    priority: int = Field(default=1, ge=1, le=10)
    expires_at: Optional[datetime] = Field(None, description="Memory expiration time")

class MemoryHistoryUpdateDto(BaseDto):
    memory_value: Optional[str] = Field(None, min_length=1)
    memory_type: Optional[str] = Field(None, max_length=50)
    priority: Optional[int] = Field(None, ge=1, le=10)
    expires_at: Optional[datetime] = None

class MemoryHistoryResponseDto(BaseDto):
    memory_id: str
    conversation_id: str
    memory_key: str
    memory_value: str
    memory_type: str
    priority: int
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class MemoryHistoryListResponseDto(BaseDto):
    memories: List[MemoryHistoryResponseDto]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool

# Chat Statistics DTOs
class ConversationStatsDto(BaseDto):
    total_conversations: int
    active_conversations: int
    archived_conversations: int
    total_messages: int
    today_messages: int
    avg_messages_per_conversation: float

class MessageStatsDto(BaseDto):
    total_messages: int
    user_messages: int
    bot_messages: int
    today_messages: int
    message_types: Dict[str, int]
    avg_message_length: float

# Search and Filter DTOs
class ConversationSearchDto(BaseDto):
    query: Optional[str] = Field(None, description="Search query")
    status: Optional[ConversationStatus] = None
    bot_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=20, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

class MessageSearchDto(BaseDto):
    query: Optional[str] = Field(None, description="Search query")
    message_type: Optional[MessageType] = None
    sender_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=20, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

# Forward references for circular imports
from .marketplace_dto import BotResponseDto

# Forward reference resolution
ConversationWithMessagesDto.model_rebuild()
MessageWithDocumentsDto.model_rebuild()

__all__ = [
    "ConversationStatus",
    "MessageType",
    "ConversationCreateDto",
    "ConversationUpdateDto",
    "ConversationResponseDto",
    "ConversationWithMessagesDto",
    "ConversationListResponseDto",
    "MessageCreateDto",
    "MessageUpdateDto",
    "MessageResponseDto",
    "MessageWithDocumentsDto",
    "MessageListResponseDto",
    "DocumentCreateDto",
    "DocumentResponseDto",
    "DocumentListResponseDto",
    "MemoryHistoryCreateDto",
    "MemoryHistoryUpdateDto",
    "MemoryHistoryResponseDto",
    "MemoryHistoryListResponseDto",
    "ConversationStatsDto",
    "MessageStatsDto",
    "ConversationSearchDto",
    "MessageSearchDto"
]