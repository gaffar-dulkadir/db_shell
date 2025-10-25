"""
SQLAlchemy models for Chat Marketplace Service
Schemas: auth, chats, marketplace
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float,
    ForeignKey, JSON, Enum as SQLEnum, TIMESTAMP, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

Base = declarative_base()

# Enums
class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    SYSTEM = "system"

class BotStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    REJECTED = "rejected"

# AUTH SCHEMA MODELS

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth'}
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_email: Mapped[str] = mapped_column(
        String(254),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_surname: Mapped[Optional[str]] = mapped_column(String(255))
    username: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='active', nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    user_created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    user_updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Properties to match service expectations
    @property
    def email(self) -> str:
        return self.user_email
    
    @email.setter
    def email(self, value: str):
        self.user_email = value
    
    @property
    def created_at(self) -> datetime:
        return self.user_created_at
    
    @property
    def updated_at(self) -> datetime:
        return self.user_updated_at
    
    @updated_at.setter
    def updated_at(self, value: datetime):
        self.user_updated_at = value
    
    # Relationships
    profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="user", uselist=False)
    settings: Mapped["UserSettings"] = relationship("UserSettings", back_populates="user", uselist=False)
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="user")

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    __table_args__ = {'schema': 'auth'}
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey('auth.users.user_id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    )
    bio: Mapped[Optional[str]] = mapped_column(Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Properties to match service expectations
    @property
    def profile_id(self) -> str:
        return self.user_id  # Use user_id as profile_id
    
    @property
    def first_name(self) -> Optional[str]:
        return None  # Not available in current schema
    
    @property
    def last_name(self) -> Optional[str]:
        return None  # Not available in current schema
    
    @property
    def display_name(self) -> Optional[str]:
        return None  # Not available in current schema
    
    @property
    def date_of_birth(self) -> Optional[datetime]:
        return None  # Not available in current schema
    
    @property
    def location(self) -> Optional[str]:
        return None  # Not available in current schema
    
    @property
    def website(self) -> Optional[str]:
        return None  # Not available in current schema
    
    @property
    def created_at(self) -> datetime:
        return self.updated_at  # Use updated_at as fallback
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")

class UserSettings(Base):
    __tablename__ = 'user_settings'
    __table_args__ = {'schema': 'auth'}
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey('auth.users.user_id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    )
    theme: Mapped[str] = mapped_column(
        String(20),
        default='dark',
        nullable=False
    )
    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    language: Mapped[str] = mapped_column(
        String(10),
        default='tr',
        nullable=False
    )
    privacy_mode: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    bot_behavior: Mapped[str] = mapped_column(
        String(255),
        default='kind',
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Properties to match service expectations
    @property
    def settings_id(self) -> str:
        return self.user_id  # Use user_id as settings_id
    
    @property
    def timezone(self) -> str:
        return 'UTC'  # Default timezone
    
    @property
    def email_notifications(self) -> bool:
        return self.notifications_enabled
    
    @property
    def push_notifications(self) -> bool:
        return self.notifications_enabled
    
    @property
    def privacy_level(self) -> str:
        return 'private' if self.privacy_mode else 'public'
    
    @property
    def two_factor_enabled(self) -> bool:
        return False  # Not available in current schema
    
    @property
    def created_at(self) -> datetime:
        return self.updated_at  # Use updated_at as fallback
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="settings")

# CHATS SCHEMA MODELS

class Conversation(Base):
    __tablename__ = 'conversation'
    __table_args__ = {'schema': 'chats'}
    
    conversation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    conversation_user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey('auth.users.user_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    conversation_bot_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey('marketplace.bots.bot_id', ondelete='CASCADE'),
        nullable=False
    )
    conversation_title: Mapped[Optional[str]] = mapped_column(String(255))
    conversation_status: Mapped[str] = mapped_column(
        String(50),
        default='active',
        nullable=False
    )
    default_system_prompt: Mapped[Optional[str]] = mapped_column(Text)
    default_knowledge: Mapped[Optional[str]] = mapped_column(Text)
    memory: Mapped[Optional[str]] = mapped_column(Text)
    custom_metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    conversation_created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    conversation_updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Properties to match service expectations
    @property
    def user_id(self) -> str:
        return self.conversation_user_id
    
    @user_id.setter
    def user_id(self, value: str):
        self.conversation_user_id = value
    
    @property
    def bot_id(self) -> str:
        return self.conversation_bot_id
    
    @bot_id.setter
    def bot_id(self, value: str):
        self.conversation_bot_id = value
    
    @property
    def title(self) -> Optional[str]:
        return self.conversation_title
    
    @title.setter
    def title(self, value: Optional[str]):
        self.conversation_title = value
    
    @property
    def status(self) -> ConversationStatus:
        return ConversationStatus(self.conversation_status)
    
    @status.setter
    def status(self, value: ConversationStatus):
        self.conversation_status = value.value
    
    @property
    def created_at(self) -> datetime:
        return self.conversation_created_at
    
    @property
    def updated_at(self) -> datetime:
        return self.conversation_updated_at
    
    @property
    @property
    def description(self) -> Optional[str]:
        return None  # Not available in current schema
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    bot: Mapped[Optional["Bot"]] = relationship("Bot", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    memory_history: Mapped[List["MemoryHistory"]] = relationship("MemoryHistory", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = 'message'
    __table_args__ = {'schema': 'chats'}
    
    message_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    message_conversation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey('chats.conversation.conversation_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    message_parent_message_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey('chats.message.message_id', ondelete='SET NULL')
    )
    message_role: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    message_bot_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey('marketplace.bots.bot_id', ondelete='CASCADE')
    )
    content: Mapped[Optional[str]] = mapped_column(Text)
    custom_metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Properties to match service expectations
    @property
    def conversation_id(self) -> str:
        return self.message_conversation_id
    
    @conversation_id.setter
    def conversation_id(self, value: str):
        self.message_conversation_id = value
    
    @property
    def parent_message_id(self) -> Optional[str]:
        return self.message_parent_message_id
    
    @parent_message_id.setter
    def parent_message_id(self, value: Optional[str]):
        self.message_parent_message_id = value
    
    @property
    def sender_type(self) -> str:
        return self.message_role
    
    @sender_type.setter
    def sender_type(self, value: str):
        self.message_role = value
    
    @property
    def sender_id(self) -> Optional[str]:
        return self.message_bot_id
    
    @sender_id.setter
    def sender_id(self, value: Optional[str]):
        self.message_bot_id = value
    
    @property
    def message_type(self) -> MessageType:
        return MessageType.TEXT  # Default to text
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    parent_message: Mapped[Optional["Message"]] = relationship("Message", remote_side="Message.message_id")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="message", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = 'document'
    __table_args__ = {'schema': 'chats'}
    
    document_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    document_uploaded_by: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey('auth.users.user_id', ondelete='CASCADE'),
        nullable=False
    )
    document_filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    document_file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    document_mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    document_content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    document_message_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey('chats.message.message_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    file_url: Mapped[Optional[str]] = mapped_column(String(500))
    custom_metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Properties to match service expectations
    @property
    def uploaded_by(self) -> str:
        return self.document_uploaded_by
    
    @uploaded_by.setter
    def uploaded_by(self, value: str):
        self.document_uploaded_by = value
    
    @property
    def file_name(self) -> str:
        return self.document_filename
    
    @file_name.setter
    def file_name(self, value: str):
        self.document_filename = value
    
    @property
    def file_size(self) -> int:
        return self.document_file_size
    
    @file_size.setter
    def file_size(self, value: int):
        self.document_file_size = value
    
    @property
    def mime_type(self) -> str:
        return self.document_mime_type
    
    @mime_type.setter
    def mime_type(self, value: str):
        self.document_mime_type = value
    
    @property
    def content(self) -> str:
        return self.document_content
    
    @content.setter
    def content(self, value: str):
        self.document_content = value
    
    @property
    def message_id(self) -> str:
        return self.document_message_id
    
    @message_id.setter
    def message_id(self, value: str):
        self.document_message_id = value
    
    @property
    def file_type(self) -> str:
        return self.document_mime_type.split('/')[0] if '/' in self.document_mime_type else 'unknown'
    
    # Relationships
    message: Mapped["Message"] = relationship("Message", back_populates="documents")

class MemoryHistory(Base):
    __tablename__ = 'memory_history'
    __table_args__ = {'schema': 'chats'}
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    conversation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey('chats.conversation.conversation_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    date_time: Mapped[datetime] = mapped_column(
        DateTime,  # timestamp without time zone
        nullable=False
    )
    memory_history: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Properties to match service expectations
    @property
    def memory_id(self) -> str:
        return self.id
    
    @property
    def memory_key(self) -> str:
        return "history"  # Default key
    
    @property
    def memory_value(self) -> str:
        return self.memory_history
    
    @memory_value.setter
    def memory_value(self, value: str):
        self.memory_history = value
    
    @property
    def memory_type(self) -> str:
        return 'context'  # Default type
    
    @property
    def priority(self) -> int:
        return 1  # Default priority
    
    @property
    def expires_at(self) -> Optional[datetime]:
        return None  # Not available in current schema
    
    @property
    def created_at(self) -> datetime:
        return self.date_time
    
    @property
    def updated_at(self) -> datetime:
        return self.date_time
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="memory_history")

# MARKETPLACE SCHEMA MODELS

class BotCategory(Base):
    __tablename__ = 'bot_categories'
    __table_args__ = {'schema': 'marketplace'}
    
    category_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    category_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )
    category_description: Mapped[Optional[str]] = mapped_column(Text)
    icon: Mapped[Optional[str]] = mapped_column(Text)
    color: Mapped[Optional[str]] = mapped_column(String(7))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Properties to match service expectations
    @property
    def name(self) -> str:
        return self.category_name
    
    @name.setter
    def name(self, value: str):
        self.category_name = value
    
    @property
    def description(self) -> Optional[str]:
        return self.category_description
    
    @description.setter
    def description(self, value: Optional[str]):
        self.category_description = value
    
    # Relationships
    bots: Mapped[List["Bot"]] = relationship("Bot", back_populates="category")

class Bot(Base):
    __tablename__ = 'bots'
    __table_args__ = {'schema': 'marketplace'}
    
    bot_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    bot_category_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey('marketplace.bot_categories.category_id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    bot_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )
    display_name: Mapped[Optional[str]] = mapped_column(String(150))
    bot_description: Mapped[Optional[str]] = mapped_column(Text)
    bot_avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    bot_status: Mapped[str] = mapped_column(
        String(50),
        default='active',
        nullable=False
    )
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rating: Mapped[Optional[float]] = mapped_column(Float)
    total_conversations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    capabilities: Mapped[Optional[dict]] = mapped_column(JSON)
    configuration: Mapped[Optional[dict]] = mapped_column(JSON)
    bot_version: Mapped[str] = mapped_column(
        String(50),
        default='1.0'
    )
    bot_owner_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey('auth.users.user_id', ondelete='CASCADE'),
        nullable=False
    )
    default_system_prompt: Mapped[Optional[str]] = mapped_column(Text)
    default_knowledge: Mapped[Optional[str]] = mapped_column(Text)
    bot_default_memory: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Properties to match service expectations
    @property
    def category_id(self) -> Optional[str]:
        return self.bot_category_id
    
    @category_id.setter
    def category_id(self, value: Optional[str]):
        self.bot_category_id = value
    
    @property
    def name(self) -> str:
        return self.bot_name
    
    @name.setter
    def name(self, value: str):
        self.bot_name = value
    
    @property
    def description(self) -> Optional[str]:
        return self.bot_description
    
    @description.setter
    def description(self, value: Optional[str]):
        self.bot_description = value
    
    @property
    def avatar_url(self) -> Optional[str]:
        return self.bot_avatar_url
    
    @avatar_url.setter
    def avatar_url(self, value: Optional[str]):
        self.bot_avatar_url = value
    
    @property
    def status(self) -> BotStatus:
        return BotStatus(self.bot_status)
    
    @status.setter
    def status(self, value: BotStatus):
        self.bot_status = value.value
    
    @property
    def created_by(self) -> Optional[str]:
        return self.bot_owner_id
    
    @created_by.setter
    def created_by(self, value: Optional[str]):
        if value:
            self.bot_owner_id = value
    
    # Relationships
    category: Mapped["BotCategory"] = relationship("BotCategory", back_populates="bots")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="bot")

# Export all models
__all__ = [
    "Base",
    "UserStatus",
    "ConversationStatus", 
    "MessageType",
    "BotStatus",
    "User",
    "UserProfile",
    "UserSettings",
    "Conversation",
    "Message",
    "Document",
    "MemoryHistory",
    "BotCategory",
    "Bot"
]