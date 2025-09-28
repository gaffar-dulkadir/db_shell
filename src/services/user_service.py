"""
User Service for Chat Marketplace Service
Handles user authentication, registration, and user management
"""

import logging
import bcrypt
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from datalayer.repository.user_repository import UserRepository, UserProfileRepository, UserSettingsRepository
from datalayer.model.sqlalchemy_models import User, UserProfile, UserSettings
from datalayer.model.dto.auth_dto import (
    UserCreateDto, UserUpdateDto, UserResponseDto, UserWithProfileDto,
    UserStatus, LoginDto, PasswordChangeDto, UserListResponseDto
)

logger = logging.getLogger(__name__)

class UserService:
    """Service for user operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.profile_repo = UserProfileRepository(session)
        self.settings_repo = UserSettingsRepository(session)
        logger.debug("✅ UserService initialized")
    
    async def create_user(self, user_data: UserCreateDto) -> UserResponseDto:
        """Create a new user with default profile and settings"""
        logger.info(f"📝 Creating new user: {user_data.email}")
        
        try:
            # Check if email already exists
            existing_user = await self.user_repo.get_by_email(user_data.email)
            if existing_user:
                raise ValueError(f"User with email {user_data.email} already exists")
            
            # Check if username already exists
            if user_data.username:
                existing_username = await self.user_repo.get_by_username(user_data.username)
                if existing_username:
                    raise ValueError(f"Username {user_data.username} already exists")
            
            # Hash password
            password_hash = self._hash_password(user_data.password)
            
            # Create user
            user = User(
                email=user_data.email.lower(),
                password_hash=password_hash,
                username=user_data.username,
                phone_number=user_data.phone_number,
                status=UserStatus.ACTIVE
            )
            
            saved_user = await self.user_repo.save(user)
            
            # Create default profile
            await self._create_default_profile(saved_user.user_id)
            
            # Create default settings
            await self._create_default_settings(saved_user.user_id)
            
            await self.session.commit()
            
            logger.info(f"✅ User created successfully: {saved_user.user_id}")
            return self._user_to_dto(saved_user)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to create user: {e}")
            raise
    
    async def authenticate_user(self, login_data: LoginDto) -> Optional[UserResponseDto]:
        """Authenticate user with email and password"""
        logger.debug(f"🔐 Authenticating user: {login_data.email}")
        
        try:
            user = await self.user_repo.get_by_email(login_data.email)
            if not user:
                logger.warning(f"⚠️ User not found: {login_data.email}")
                return None
            
            if not self._verify_password(login_data.password, user.password_hash):
                logger.warning(f"⚠️ Invalid password for user: {login_data.email}")
                return None
            
            if user.status != UserStatus.ACTIVE:
                logger.warning(f"⚠️ User account is not active: {login_data.email}")
                return None
            
            # Update last login
            await self.user_repo.update_last_login(user.user_id)
            await self.session.commit()
            
            logger.info(f"✅ User authenticated successfully: {user.user_id}")
            return self._user_to_dto(user)
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            raise
    
    async def get_user_by_id(self, user_id: str, include_profile: bool = False) -> Optional[UserResponseDto]:
        """Get user by ID"""
        logger.debug(f"🔍 Getting user by ID: {user_id}")
        
        try:
            if include_profile:
                user = await self.user_repo.get_with_profile_and_settings(user_id)
                if user:
                    return self._user_with_profile_to_dto(user)
            else:
                user = await self.user_repo.get_by_id(user_id)
                if user:
                    return self._user_to_dto(user)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get user: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponseDto]:
        """Get user by email"""
        logger.debug(f"🔍 Getting user by email: {email}")
        
        try:
            user = await self.user_repo.get_by_email(email)
            return self._user_to_dto(user) if user else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get user by email: {e}")
            raise
    
    async def get_user_by_username(self, username: str) -> Optional[UserResponseDto]:
        """Get user by username"""
        logger.debug(f"🔍 Getting user by username: {username}")
        
        try:
            user = await self.user_repo.get_by_username(username)
            return self._user_to_dto(user) if user else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get user by username: {e}")
            raise
    
    async def update_user(self, user_id: str, update_data: UserUpdateDto) -> Optional[UserResponseDto]:
        """Update user information"""
        logger.info(f"📝 Updating user: {user_id}")
        
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return None
            
            # Check username uniqueness if changing
            if update_data.username and update_data.username != user.username:
                existing_user = await self.user_repo.get_by_username(update_data.username)
                if existing_user and existing_user.user_id != user_id:
                    raise ValueError(f"Username {update_data.username} already exists")
            
            # Update fields
            if update_data.username is not None:
                user.username = update_data.username
            if update_data.phone_number is not None:
                user.phone_number = update_data.phone_number
            if update_data.status is not None:
                user.status = update_data.status
            
            user.updated_at = datetime.utcnow()
            
            updated_user = await self.user_repo.save(user)
            await self.session.commit()
            
            logger.info(f"✅ User updated successfully: {user_id}")
            return self._user_to_dto(updated_user)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to update user: {e}")
            raise
    
    async def change_password(self, user_id: str, password_data: PasswordChangeDto) -> bool:
        """Change user password"""
        logger.info(f"🔐 Changing password for user: {user_id}")
        
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return False
            
            # Verify current password
            if not self._verify_password(password_data.current_password, user.password_hash):
                logger.warning(f"⚠️ Invalid current password for user: {user_id}")
                return False
            
            # Hash new password
            new_password_hash = self._hash_password(password_data.new_password)
            user.password_hash = new_password_hash
            user.updated_at = datetime.utcnow()
            
            await self.user_repo.save(user)
            await self.session.commit()
            
            logger.info(f"✅ Password changed successfully for user: {user_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to change password: {e}")
            raise
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        logger.info(f"⚠️ Deactivating user: {user_id}")
        
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return False
            
            user.status = UserStatus.INACTIVE
            user.updated_at = datetime.utcnow()
            
            await self.user_repo.save(user)
            await self.session.commit()
            
            logger.info(f"✅ User deactivated successfully: {user_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to deactivate user: {e}")
            raise
    
    async def verify_user_email(self, user_id: str) -> bool:
        """Mark user email as verified"""
        logger.info(f"✅ Verifying email for user: {user_id}")
        
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return False
            
            user.is_verified = True
            user.updated_at = datetime.utcnow()
            
            await self.user_repo.save(user)
            await self.session.commit()
            
            logger.info(f"✅ Email verified successfully for user: {user_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to verify email: {e}")
            raise
    
    async def search_users(
        self, 
        query: str, 
        status: Optional[UserStatus] = None,
        limit: int = 20, 
        offset: int = 0
    ) -> UserListResponseDto:
        """Search users"""
        logger.debug(f"🔍 Searching users: {query}")
        
        try:
            users = await self.user_repo.search_users(query, status, limit + 1, offset)
            
            # Check if there are more results
            has_next = len(users) > limit
            if has_next:
                users = users[:limit]
            
            has_prev = offset > 0
            
            # Get total count for accurate pagination
            all_users = await self.user_repo.search_users(query, status, 1000, 0)
            total = len(all_users)
            
            user_dtos = [self._user_to_dto(user) for user in users]
            
            return UserListResponseDto(
                users=user_dtos,
                total=total,
                page=(offset // limit) + 1,
                limit=limit,
                has_next=has_next,
                has_prev=has_prev
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to search users: {e}")
            raise
    
    async def get_users_by_status(
        self, 
        status: UserStatus, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[UserResponseDto]:
        """Get users by status"""
        logger.debug(f"🔍 Getting users by status: {status}")
        
        try:
            users = await self.user_repo.find_by_status(status, limit, offset)
            return [self._user_to_dto(user) for user in users]
            
        except Exception as e:
            logger.error(f"❌ Failed to get users by status: {e}")
            raise
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        logger.debug("📊 Getting user statistics")
        
        try:
            stats = await self.user_repo.get_user_stats()
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get user stats: {e}")
            raise
    
    async def _create_default_profile(self, user_id: str) -> UserProfile:
        """Create default profile for new user"""
        profile = UserProfile(user_id=user_id)
        return await self.profile_repo.save(profile)
    
    async def _create_default_settings(self, user_id: str) -> UserSettings:
        """Create default settings for new user"""
        settings = UserSettings(user_id=user_id)
        return await self.settings_repo.save(settings)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def _user_to_dto(self, user: User) -> UserResponseDto:
        """Convert User model to UserResponseDto"""
        return UserResponseDto(
            user_id=user.user_id,
            email=user.email,
            username=user.username,
            phone_number=user.phone_number,
            is_verified=user.is_verified,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )
    
    def _user_with_profile_to_dto(self, user: User) -> UserWithProfileDto:
        """Convert User model with relationships to UserWithProfileDto"""
        from .profile_service import ProfileService
        from .settings_service import SettingsService
        
        user_dto = self._user_to_dto(user)
        profile_dto = None
        settings_dto = None
        
        if user.profile:
            profile_dto = ProfileService._profile_to_dto(user.profile)
        
        if user.settings:
            settings_dto = SettingsService._settings_to_dto(user.settings)
        
        return UserWithProfileDto(
            **user_dto.dict(),
            profile=profile_dto,
            settings=settings_dto
        )

__all__ = ["UserService"]