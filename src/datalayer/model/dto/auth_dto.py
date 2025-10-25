"""
Auth DTOs for Chat Marketplace Service
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum
from .base_dto import BaseDto

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

# User DTOs
class UserCreateDto(BaseDto):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    user_name: str = Field(..., min_length=1, max_length=255, description="First name")
    user_surname: Optional[str] = Field(None, max_length=255, description="Last name")
    username: Optional[str] = Field(None, min_length=3, max_length=100, description="Unique username")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")

    @validator('email')
    def email_must_be_lowercase(cls, v):
        return v.lower()

    @validator('username')
    def username_alphanumeric(cls, v):
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters, hyphens, and underscores')
        return v.lower() if v else v

    @validator('user_name')
    def validate_user_name(cls, v):
        return v.strip()

    @validator('user_surname')
    def validate_user_surname(cls, v):
        return v.strip() if v else v

class UserUpdateDto(BaseDto):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    status: Optional[UserStatus] = None

class UserResponseDto(BaseDto):
    user_id: str
    email: str
    user_name: str
    user_surname: Optional[str] = None
    username: Optional[str] = None
    phone_number: Optional[str] = None
    is_verified: bool
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

class UserWithProfileDto(UserResponseDto):
    profile: Optional["UserProfileResponseDto"] = None
    settings: Optional["UserSettingsResponseDto"] = None

# User Profile DTOs
class UserProfileCreateDto(BaseDto):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=150)
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = Field(None, max_length=500)
    date_of_birth: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=300)

class UserProfileUpdateDto(BaseDto):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=150)
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = Field(None, max_length=500)
    date_of_birth: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=300)

class UserProfileResponseDto(BaseDto):
    profile_id: str
    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    location: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# User Settings DTOs
class UserSettingsCreateDto(BaseDto):
    language: str = Field(default='en', max_length=10)
    timezone: str = Field(default='UTC', max_length=50)
    email_notifications: bool = Field(default=True)
    push_notifications: bool = Field(default=True)
    privacy_level: str = Field(default='public', max_length=20)
    theme: str = Field(default='light', max_length=20)
    two_factor_enabled: bool = Field(default=False)

class UserSettingsUpdateDto(BaseDto):
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    privacy_level: Optional[str] = Field(None, max_length=20)
    theme: Optional[str] = Field(None, max_length=20)
    two_factor_enabled: Optional[bool] = None

class UserSettingsResponseDto(BaseDto):
    settings_id: str
    user_id: str
    language: str
    timezone: str
    email_notifications: bool
    push_notifications: bool
    privacy_level: str
    theme: str
    two_factor_enabled: bool
    created_at: datetime
    updated_at: datetime

# Authentication DTOs
class LoginDto(BaseDto):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @validator('email')
    def email_must_be_lowercase(cls, v):
        return v.lower()

# TokenResponseDto removed - not using JWT tokens for simple authentication

class PasswordChangeDto(BaseDto):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")

class PasswordResetRequestDto(BaseDto):
    email: str = Field(..., description="User email address")

    @validator('email')
    def email_must_be_lowercase(cls, v):
        return v.lower()

class PasswordResetDto(BaseDto):
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")

# Pagination DTOs
class UserListResponseDto(BaseDto):
    users: list[UserResponseDto]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool

# Forward reference resolution
UserWithProfileDto.model_rebuild()

__all__ = [
    "UserStatus",
    "UserCreateDto",
    "UserUpdateDto", 
    "UserResponseDto",
    "UserWithProfileDto",
    "UserProfileCreateDto",
    "UserProfileUpdateDto",
    "UserProfileResponseDto",
    "UserSettingsCreateDto",
    "UserSettingsUpdateDto",
    "UserSettingsResponseDto",
    "LoginDto",
    "PasswordChangeDto",
    "PasswordResetRequestDto",
    "PasswordResetDto",
    "UserListResponseDto"
]