"""
Settings Service for Chat Marketplace Service
Handles user settings operations
"""

import logging
from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from datalayer.repository.user_repository import UserSettingsRepository
from datalayer.model.sqlalchemy_models import UserSettings
from datalayer.model.dto.auth_dto import (
    UserSettingsCreateDto, UserSettingsUpdateDto, UserSettingsResponseDto
)

logger = logging.getLogger(__name__)

class SettingsService:
    """Service for user settings operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.settings_repo = UserSettingsRepository(session)
        logger.debug("✅ SettingsService initialized")
    
    async def create_settings(self, user_id: str, settings_data: UserSettingsCreateDto) -> UserSettingsResponseDto:
        """Create user settings"""
        logger.info(f"📝 Creating settings for user: {user_id}")
        
        try:
            # Check if settings already exist
            existing_settings = await self.settings_repo.get_by_user_id(user_id)
            if existing_settings:
                raise ValueError(f"Settings already exist for user {user_id}")
            
            # Create settings
            settings = UserSettings(
                user_id=user_id,
                language=settings_data.language,
                timezone=settings_data.timezone,
                email_notifications=settings_data.email_notifications,
                push_notifications=settings_data.push_notifications,
                privacy_level=settings_data.privacy_level,
                theme=settings_data.theme,
                two_factor_enabled=settings_data.two_factor_enabled
            )
            
            saved_settings = await self.settings_repo.save(settings)
            await self.session.commit()
            
            logger.info(f"✅ Settings created successfully for user: {user_id}")
            return self._settings_to_dto(saved_settings)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to create settings: {e}")
            raise
    
    async def get_settings_by_user_id(self, user_id: str) -> Optional[UserSettingsResponseDto]:
        """Get user settings by user ID"""
        logger.debug(f"🔍 Getting settings for user: {user_id}")
        
        try:
            settings = await self.settings_repo.get_by_user_id(user_id)
            return self._settings_to_dto(settings) if settings else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get settings: {e}")
            raise
    
    async def get_settings_by_id(self, settings_id: str) -> Optional[UserSettingsResponseDto]:
        """Get settings by settings ID"""
        logger.debug(f"🔍 Getting settings by ID: {settings_id}")
        
        try:
            settings = await self.settings_repo.get_by_id(settings_id)
            return self._settings_to_dto(settings) if settings else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get settings by ID: {e}")
            raise
    
    async def update_settings(self, user_id: str, update_data: UserSettingsUpdateDto) -> Optional[UserSettingsResponseDto]:
        """Update user settings"""
        logger.info(f"📝 Updating settings for user: {user_id}")
        
        try:
            settings = await self.settings_repo.get_by_user_id(user_id)
            if not settings:
                logger.warning(f"⚠️ Settings not found for user: {user_id}")
                return None
            
            # Update fields
            if update_data.language is not None:
                settings.language = update_data.language
            if update_data.timezone is not None:
                settings.timezone = update_data.timezone
            if update_data.email_notifications is not None:
                settings.email_notifications = update_data.email_notifications
            if update_data.push_notifications is not None:
                settings.push_notifications = update_data.push_notifications
            if update_data.privacy_level is not None:
                settings.privacy_level = update_data.privacy_level
            if update_data.theme is not None:
                settings.theme = update_data.theme
            if update_data.two_factor_enabled is not None:
                settings.two_factor_enabled = update_data.two_factor_enabled
            
            settings.updated_at = datetime.utcnow()
            
            updated_settings = await self.settings_repo.save(settings)
            await self.session.commit()
            
            logger.info(f"✅ Settings updated successfully for user: {user_id}")
            return self._settings_to_dto(updated_settings)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to update settings: {e}")
            raise
    
    async def update_notification_settings(
        self, 
        user_id: str, 
        email_notifications: Optional[bool] = None,
        push_notifications: Optional[bool] = None
    ) -> Optional[UserSettingsResponseDto]:
        """Update notification settings"""
        logger.info(f"🔔 Updating notification settings for user: {user_id}")
        
        try:
            success = await self.settings_repo.update_notification_settings(
                user_id, email_notifications, push_notifications
            )
            
            if not success:
                return None
            
            # Get updated settings
            settings = await self.settings_repo.get_by_user_id(user_id)
            return self._settings_to_dto(settings) if settings else None
            
        except Exception as e:
            logger.error(f"❌ Failed to update notification settings: {e}")
            raise
    
    async def update_theme(self, user_id: str, theme: str) -> Optional[UserSettingsResponseDto]:
        """Update user theme"""
        logger.info(f"🎨 Updating theme for user: {user_id} to {theme}")
        
        try:
            settings = await self.settings_repo.get_by_user_id(user_id)
            if not settings:
                return None
            
            settings.theme = theme
            settings.updated_at = datetime.utcnow()
            
            updated_settings = await self.settings_repo.save(settings)
            await self.session.commit()
            
            logger.info(f"✅ Theme updated successfully for user: {user_id}")
            return self._settings_to_dto(updated_settings)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to update theme: {e}")
            raise
    
    async def update_language(self, user_id: str, language: str) -> Optional[UserSettingsResponseDto]:
        """Update user language"""
        logger.info(f"🌐 Updating language for user: {user_id} to {language}")
        
        try:
            settings = await self.settings_repo.get_by_user_id(user_id)
            if not settings:
                return None
            
            settings.language = language
            settings.updated_at = datetime.utcnow()
            
            updated_settings = await self.settings_repo.save(settings)
            await self.session.commit()
            
            logger.info(f"✅ Language updated successfully for user: {user_id}")
            return self._settings_to_dto(updated_settings)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to update language: {e}")
            raise
    
    async def toggle_two_factor(self, user_id: str, enabled: bool) -> Optional[UserSettingsResponseDto]:
        """Toggle two-factor authentication"""
        logger.info(f"🔐 {'Enabling' if enabled else 'Disabling'} 2FA for user: {user_id}")
        
        try:
            settings = await self.settings_repo.get_by_user_id(user_id)
            if not settings:
                return None
            
            settings.two_factor_enabled = enabled
            settings.updated_at = datetime.utcnow()
            
            updated_settings = await self.settings_repo.save(settings)
            await self.session.commit()
            
            logger.info(f"✅ 2FA {'enabled' if enabled else 'disabled'} for user: {user_id}")
            return self._settings_to_dto(updated_settings)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to toggle 2FA: {e}")
            raise
    
    async def get_users_with_email_notifications(self) -> List[UserSettingsResponseDto]:
        """Get all users with email notifications enabled"""
        logger.debug("📧 Getting users with email notifications enabled")
        
        try:
            settings_list = await self.settings_repo.get_users_with_email_notifications()
            return [self._settings_to_dto(settings) for settings in settings_list]
            
        except Exception as e:
            logger.error(f"❌ Failed to get users with email notifications: {e}")
            raise
    
    async def reset_to_defaults(self, user_id: str) -> Optional[UserSettingsResponseDto]:
        """Reset user settings to defaults"""
        logger.info(f"🔄 Resetting settings to defaults for user: {user_id}")
        
        try:
            settings = await self.settings_repo.get_by_user_id(user_id)
            if not settings:
                return None
            
            # Reset to default values
            settings.language = 'en'
            settings.timezone = 'UTC'
            settings.email_notifications = True
            settings.push_notifications = True
            settings.privacy_level = 'public'
            settings.theme = 'light'
            settings.two_factor_enabled = False
            settings.updated_at = datetime.utcnow()
            
            updated_settings = await self.settings_repo.save(settings)
            await self.session.commit()
            
            logger.info(f"✅ Settings reset to defaults for user: {user_id}")
            return self._settings_to_dto(updated_settings)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to reset settings: {e}")
            raise
    
    async def delete_settings(self, user_id: str) -> bool:
        """Delete user settings"""
        logger.info(f"🗑️ Deleting settings for user: {user_id}")
        
        try:
            settings = await self.settings_repo.get_by_user_id(user_id)
            if not settings:
                return False
            
            await self.settings_repo.delete(settings)
            await self.session.commit()
            
            logger.info(f"✅ Settings deleted successfully for user: {user_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to delete settings: {e}")
            raise
    
    @staticmethod
    def _settings_to_dto(settings: UserSettings) -> UserSettingsResponseDto:
        """Convert UserSettings model to UserSettingsResponseDto"""
        return UserSettingsResponseDto(
            settings_id=settings.settings_id,
            user_id=settings.user_id,
            language=settings.language,
            timezone=settings.timezone,
            email_notifications=settings.email_notifications,
            push_notifications=settings.push_notifications,
            privacy_level=settings.privacy_level,
            theme=settings.theme,
            two_factor_enabled=settings.two_factor_enabled,
            created_at=settings.created_at,
            updated_at=settings.updated_at
        )

__all__ = ["SettingsService"]