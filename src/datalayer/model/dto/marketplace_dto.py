"""
Marketplace DTOs for Chat Marketplace Service
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from .base_dto import BaseDto

class BotStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    REJECTED = "rejected"

# Bot Category DTOs
class BotCategoryCreateDto(BaseDto):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=1000, description="Category description")
    icon: Optional[str] = Field(None, max_length=100, description="Category icon")
    color: Optional[str] = Field(None, min_length=7, max_length=7, description="Hex color code")
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0, ge=0, description="Sort order for display")

    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            raise ValueError('Color must be a valid hex color code starting with #')
        return v

    @validator('name')
    def validate_name(cls, v):
        return v.strip()

class BotCategoryUpdateDto(BaseDto):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    icon: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, min_length=7, max_length=7)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)

    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            raise ValueError('Color must be a valid hex color code starting with #')
        return v

    @validator('name')
    def validate_name(cls, v):
        if v:
            return v.strip()
        return v

class BotCategoryResponseDto(BaseDto):
    category_id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: bool
    sort_order: int
    bot_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

class BotCategoryWithBotsDto(BotCategoryResponseDto):
    bots: List["BotResponseDto"] = []

class BotCategoryListResponseDto(BaseDto):
    categories: List[BotCategoryResponseDto]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool

# Bot DTOs
class BotCreateDto(BaseDto):
    category_id: str = Field(..., description="Bot category ID")
    name: str = Field(..., min_length=1, max_length=100, description="Bot unique name")
    display_name: str = Field(..., min_length=1, max_length=150, description="Bot display name")
    description: str = Field(..., min_length=1, max_length=5000, description="Bot description")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Bot avatar URL")
    is_featured: bool = Field(default=False)
    is_premium: bool = Field(default=False)
    capabilities: Optional[Dict[str, Any]] = Field(None, description="Bot capabilities")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Bot configuration")

    @validator('name')
    def validate_name(cls, v):
        # Bot name should be URL-friendly
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Bot name must contain only alphanumeric characters, hyphens, and underscores')
        return v.lower()

    @validator('display_name')
    def validate_display_name(cls, v):
        return v.strip()

class BotUpdateDto(BaseDto):
    category_id: Optional[str] = None
    display_name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    avatar_url: Optional[str] = Field(None, max_length=500)
    status: Optional[BotStatus] = None
    is_featured: Optional[bool] = None
    is_premium: Optional[bool] = None
    capabilities: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None

    @validator('display_name')
    def validate_display_name(cls, v):
        if v:
            return v.strip()
        return v

class BotResponseDto(BaseDto):
    bot_id: str
    category_id: str
    name: str
    display_name: str
    description: str
    avatar_url: Optional[str] = None
    status: BotStatus
    is_featured: bool
    is_premium: bool
    rating: Optional[float] = None
    total_conversations: int
    capabilities: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class BotWithCategoryDto(BotResponseDto):
    category: Optional[BotCategoryResponseDto] = None

class BotListResponseDto(BaseDto):
    bots: List[BotResponseDto]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool

class BotDetailDto(BotResponseDto):
    category: BotCategoryResponseDto
    conversation_count: int
    recent_conversations: Optional[int] = 0  # Conversations in last 30 days

# Bot Statistics DTOs
class BotStatsDto(BaseDto):
    total_bots: int
    active_bots: int
    pending_bots: int
    featured_bots: int
    premium_bots: int
    bots_by_category: Dict[str, int]
    top_rated_bots: List[BotResponseDto]
    most_used_bots: List[BotResponseDto]

class CategoryStatsDto(BaseDto):
    total_categories: int
    active_categories: int
    categories_with_bots: int
    bots_per_category: Dict[str, int]

# Search and Filter DTOs
class BotSearchDto(BaseDto):
    query: Optional[str] = Field(None, description="Search query")
    category_id: Optional[str] = None
    status: Optional[BotStatus] = None
    is_featured: Optional[bool] = None
    is_premium: Optional[bool] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    sort_by: Optional[str] = Field(default='name', description="Sort field")
    sort_order: Optional[str] = Field(default='asc', description="Sort order: asc, desc")
    limit: int = Field(default=20, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_fields = ['name', 'display_name', 'rating', 'total_conversations', 'created_at', 'updated_at']
        if v not in allowed_fields:
            raise ValueError(f'sort_by must be one of: {", ".join(allowed_fields)}')
        return v

    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('sort_order must be "asc" or "desc"')
        return v

class CategorySearchDto(BaseDto):
    query: Optional[str] = Field(None, description="Search query")
    is_active: Optional[bool] = None
    has_bots: Optional[bool] = Field(None, description="Filter categories that have bots")
    sort_by: Optional[str] = Field(default='sort_order', description="Sort field")
    sort_order: Optional[str] = Field(default='asc', description="Sort order: asc, desc")
    limit: int = Field(default=20, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_fields = ['name', 'sort_order', 'created_at', 'updated_at']
        if v not in allowed_fields:
            raise ValueError(f'sort_by must be one of: {", ".join(allowed_fields)}')
        return v

    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('sort_order must be "asc" or "desc"')
        return v

# Bot Configuration DTOs
class BotCapabilityDto(BaseDto):
    name: str
    description: str
    enabled: bool = True
    configuration: Optional[Dict[str, Any]] = None

class BotConfigurationDto(BaseDto):
    model_name: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, gt=0)
    system_prompt: Optional[str] = None
    capabilities: List[BotCapabilityDto] = []
    custom_settings: Optional[Dict[str, Any]] = None

# Forward reference resolution
BotCategoryWithBotsDto.model_rebuild()

__all__ = [
    "BotStatus",
    "BotCategoryCreateDto",
    "BotCategoryUpdateDto",
    "BotCategoryResponseDto",
    "BotCategoryWithBotsDto",
    "BotCategoryListResponseDto",
    "BotCreateDto",
    "BotUpdateDto",
    "BotResponseDto",
    "BotWithCategoryDto",
    "BotListResponseDto",
    "BotDetailDto",
    "BotStatsDto",
    "CategoryStatsDto",
    "BotSearchDto",
    "CategorySearchDto",
    "BotCapabilityDto",
    "BotConfigurationDto"
]