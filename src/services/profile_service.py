"""
Profile Service for Chat Marketplace Service
Handles user profile operations
"""

import logging
from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from datalayer.repository.user_repository import UserProfileRepository
from datalayer.model.sqlalchemy_models import UserProfile
from datalayer.model.dto.auth_dto import (
    UserProfileCreateDto, UserProfileUpdateDto, UserProfileResponseDto
)

logger = logging.getLogger(__name__)

class ProfileService:
    """Service for user profile operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.profile_repo = UserProfileRepository(session)
        logger.debug("✅ ProfileService initialized")
    
    async def create_profile(self, user_id: str, profile_data: UserProfileCreateDto) -> UserProfileResponseDto:
        """Create user profile"""
        logger.info(f"📝 Creating profile for user: {user_id}")
        
        try:
            # Check if profile already exists
            existing_profile = await self.profile_repo.get_by_user_id(user_id)
            if existing_profile:
                raise ValueError(f"Profile already exists for user {user_id}")
            
            # Create profile
            profile = UserProfile(
                user_id=user_id,
                first_name=profile_data.first_name,
                last_name=profile_data.last_name,
                display_name=profile_data.display_name,
                bio=profile_data.bio,
                avatar_url=profile_data.avatar_url,
                date_of_birth=profile_data.date_of_birth,
                location=profile_data.location,
                website=profile_data.website
            )
            
            saved_profile = await self.profile_repo.save(profile)
            await self.session.commit()
            
            logger.info(f"✅ Profile created successfully for user: {user_id}")
            return self._profile_to_dto(saved_profile)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to create profile: {e}")
            raise
    
    async def get_profile_by_user_id(self, user_id: str) -> Optional[UserProfileResponseDto]:
        """Get user profile by user ID"""
        logger.debug(f"🔍 Getting profile for user: {user_id}")
        
        try:
            profile = await self.profile_repo.get_by_user_id(user_id)
            return self._profile_to_dto(profile) if profile else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get profile: {e}")
            raise
    
    async def get_profile_by_id(self, profile_id: str) -> Optional[UserProfileResponseDto]:
        """Get profile by profile ID"""
        logger.debug(f"🔍 Getting profile by ID: {profile_id}")
        
        try:
            profile = await self.profile_repo.get_by_id(profile_id)
            return self._profile_to_dto(profile) if profile else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get profile by ID: {e}")
            raise
    
    async def update_profile(self, user_id: str, update_data: UserProfileUpdateDto) -> Optional[UserProfileResponseDto]:
        """Update user profile"""
        logger.info(f"📝 Updating profile for user: {user_id}")
        
        try:
            profile = await self.profile_repo.get_by_user_id(user_id)
            if not profile:
                logger.warning(f"⚠️ Profile not found for user: {user_id}")
                return None
            
            # Update fields
            if update_data.first_name is not None:
                profile.first_name = update_data.first_name
            if update_data.last_name is not None:
                profile.last_name = update_data.last_name
            if update_data.display_name is not None:
                profile.display_name = update_data.display_name
            if update_data.bio is not None:
                profile.bio = update_data.bio
            if update_data.avatar_url is not None:
                profile.avatar_url = update_data.avatar_url
            if update_data.date_of_birth is not None:
                profile.date_of_birth = update_data.date_of_birth
            if update_data.location is not None:
                profile.location = update_data.location
            if update_data.website is not None:
                profile.website = update_data.website
            
            profile.updated_at = datetime.utcnow()
            
            updated_profile = await self.profile_repo.save(profile)
            await self.session.commit()
            
            logger.info(f"✅ Profile updated successfully for user: {user_id}")
            return self._profile_to_dto(updated_profile)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to update profile: {e}")
            raise
    
    async def update_avatar(self, user_id: str, avatar_url: str) -> Optional[UserProfileResponseDto]:
        """Update user avatar"""
        logger.info(f"🖼️ Updating avatar for user: {user_id}")
        
        try:
            profile = await self.profile_repo.get_by_user_id(user_id)
            if not profile:
                return None
            
            profile.avatar_url = avatar_url
            profile.updated_at = datetime.utcnow()
            
            updated_profile = await self.profile_repo.save(profile)
            await self.session.commit()
            
            logger.info(f"✅ Avatar updated successfully for user: {user_id}")
            return self._profile_to_dto(updated_profile)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to update avatar: {e}")
            raise
    
    async def search_profiles(self, query: str, limit: int = 20, offset: int = 0) -> list[UserProfileResponseDto]:
        """Search profiles by name"""
        logger.debug(f"🔍 Searching profiles: {query}")
        
        try:
            profiles = await self.profile_repo.search_by_name(query, limit, offset)
            return [self._profile_to_dto(profile) for profile in profiles]
            
        except Exception as e:
            logger.error(f"❌ Failed to search profiles: {e}")
            raise
    
    async def delete_profile(self, user_id: str) -> bool:
        """Delete user profile"""
        logger.info(f"🗑️ Deleting profile for user: {user_id}")
        
        try:
            profile = await self.profile_repo.get_by_user_id(user_id)
            if not profile:
                return False
            
            await self.profile_repo.delete(profile)
            await self.session.commit()
            
            logger.info(f"✅ Profile deleted successfully for user: {user_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to delete profile: {e}")
            raise
    
    @staticmethod
    def _profile_to_dto(profile: UserProfile) -> UserProfileResponseDto:
        """Convert UserProfile model to UserProfileResponseDto"""
        return UserProfileResponseDto(
            profile_id=profile.profile_id,
            user_id=profile.user_id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            display_name=profile.display_name,
            bio=profile.bio,
            avatar_url=profile.avatar_url,
            date_of_birth=profile.date_of_birth,
            location=profile.location,
            website=profile.website,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )

__all__ = ["ProfileService"]