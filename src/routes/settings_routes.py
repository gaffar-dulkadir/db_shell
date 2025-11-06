"""
Settings Routes for Chat Marketplace Service
Handles user settings management endpoints
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status

from datalayer.database import get_postgres_session
from sqlalchemy.ext.asyncio import AsyncSession
from services.settings_service import SettingsService
from datalayer.model.dto.auth_dto import (
    UserSettingsCreateDto, UserSettingsUpdateDto, UserSettingsResponseDto
)

logger = logging.getLogger(__name__)

# Router configuration
router = APIRouter(
    prefix="/users/{user_id}/settings",
    tags=["User Settings"],
    responses={404: {"description": "Not found"}}
)

# Dependency functions
def get_settings_service(session: AsyncSession = Depends(get_postgres_session)) -> SettingsService:
    """Settings service dependency"""
    return SettingsService(session)

# Helper functions to avoid code duplication
async def _create_settings_impl(
    user_id: str,
    settings_data: UserSettingsCreateDto,
    settings_service: SettingsService
):
    """Implementation for create settings"""
    logger.info(f"🚀 API: Create settings requested for user: {user_id}")
    
    try:
        settings = await settings_service.create_settings(user_id, settings_data)
        logger.info(f"✅ API: Settings created successfully: {settings.settings_id}")
        return settings
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Settings creation validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ API: Settings creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create settings")

async def _get_settings_impl(
    user_id: str,
    settings_service: SettingsService
):
    """Implementation for get settings"""
    logger.info(f"🚀 API: Get settings requested for user: {user_id}")
    
    try:
        settings = await settings_service.get_settings_by_user_id(user_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        logger.info(f"✅ API: Settings retrieved: {settings.settings_id}")
        return settings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to get settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get settings")

async def _update_settings_impl(
    user_id: str,
    update_data: UserSettingsUpdateDto,
    settings_service: SettingsService
):
    """Implementation for update settings"""
    logger.info(f"🚀 API: Update settings requested for user: {user_id}")
    
    try:
        settings = await settings_service.update_settings(user_id, update_data)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        logger.info(f"✅ API: Settings updated successfully: {settings.settings_id}")
        return settings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to update settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings")

@router.post(
    "/",
    response_model=UserSettingsResponseDto,
    status_code=status.HTTP_201_CREATED,
    summary="Create user settings",
    description="Create new user settings"
)
async def create_settings(
    user_id: str,
    settings_data: UserSettingsCreateDto,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Create user settings (without trailing slash)"""
    return await _create_settings_impl(user_id, settings_data, settings_service)

@router.post(
    "",
    response_model=UserSettingsResponseDto,
    status_code=status.HTTP_201_CREATED,
    summary="Create user settings",
    description="Create new user settings",
    include_in_schema=False
)
async def create_settings_no_slash(
    user_id: str,
    settings_data: UserSettingsCreateDto,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Create user settings (with trailing slash)"""
    return await _create_settings_impl(user_id, settings_data, settings_service)

@router.get(
    "/",
    response_model=UserSettingsResponseDto,
    summary="Get user settings",
    description="Get user settings information"
)
async def get_settings(
    user_id: str,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Get user settings (without trailing slash)"""
    return await _get_settings_impl(user_id, settings_service)

@router.get(
    "",
    response_model=UserSettingsResponseDto,
    summary="Get user settings",
    description="Get user settings information",
    include_in_schema=False
)
async def get_settings_no_slash(
    user_id: str,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Get user settings (with trailing slash)"""
    return await _get_settings_impl(user_id, settings_service)

@router.put(
    "/",
    response_model=UserSettingsResponseDto,
    summary="Update user settings",
    description="Update user settings information"
)
async def update_settings(
    user_id: str,
    update_data: UserSettingsUpdateDto,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Update user settings (without trailing slash)"""
    return await _update_settings_impl(user_id, update_data, settings_service)

@router.put(
    "",
    response_model=UserSettingsResponseDto,
    summary="Update user settings",
    description="Update user settings information",
    include_in_schema=False
)
async def update_settings_no_slash(
    user_id: str,
    update_data: UserSettingsUpdateDto,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Update user settings (with trailing slash)"""
    return await _update_settings_impl(user_id, update_data, settings_service)

@router.patch(
    "/notifications",
    response_model=UserSettingsResponseDto,
    summary="Update notification settings",
    description="Update email and push notification settings"
)
async def update_notification_settings(
    user_id: str,
    email_notifications: bool = Query(None, description="Enable email notifications"),
    push_notifications: bool = Query(None, description="Enable push notifications"),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Update notification settings"""
    logger.info(f"🚀 API: Update notification settings requested for user: {user_id}")
    
    try:
        settings = await settings_service.update_notification_settings(
            user_id, email_notifications, push_notifications
        )
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        logger.info(f"✅ API: Notification settings updated successfully for user: {user_id}")
        return settings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to update notification settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update notification settings")

@router.patch(
    "/theme",
    response_model=UserSettingsResponseDto,
    summary="Update theme",
    description="Update user theme preference"
)
async def update_theme(
    user_id: str,
    theme: str = Query(..., description="Theme name (e.g., light, dark)"),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Update user theme"""
    logger.info(f"🚀 API: Update theme requested for user: {user_id}")
    
    try:
        settings = await settings_service.update_theme(user_id, theme)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        logger.info(f"✅ API: Theme updated successfully for user: {user_id}")
        return settings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to update theme: {e}")
        raise HTTPException(status_code=500, detail="Failed to update theme")

@router.patch(
    "/language",
    response_model=UserSettingsResponseDto,
    summary="Update language",
    description="Update user language preference"
)
async def update_language(
    user_id: str,
    language: str = Query(..., description="Language code (e.g., en, tr)"),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Update user language"""
    logger.info(f"🚀 API: Update language requested for user: {user_id}")
    
    try:
        settings = await settings_service.update_language(user_id, language)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        logger.info(f"✅ API: Language updated successfully for user: {user_id}")
        return settings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to update language: {e}")
        raise HTTPException(status_code=500, detail="Failed to update language")

@router.patch(
    "/two-factor",
    response_model=UserSettingsResponseDto,
    summary="Toggle two-factor authentication",
    description="Enable or disable two-factor authentication"
)
async def toggle_two_factor(
    user_id: str,
    enabled: bool = Query(..., description="Enable two-factor authentication"),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Toggle two-factor authentication"""
    logger.info(f"🚀 API: Toggle 2FA requested for user: {user_id}")
    
    try:
        settings = await settings_service.toggle_two_factor(user_id, enabled)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        logger.info(f"✅ API: 2FA toggled successfully for user: {user_id}")
        return settings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to toggle 2FA: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle two-factor authentication")

@router.post(
    "/reset",
    response_model=UserSettingsResponseDto,
    summary="Reset settings to defaults",
    description="Reset user settings to default values"
)
async def reset_settings(
    user_id: str,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Reset settings to defaults"""
    logger.info(f"🚀 API: Reset settings requested for user: {user_id}")
    
    try:
        settings = await settings_service.reset_to_defaults(user_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        logger.info(f"✅ API: Settings reset successfully for user: {user_id}")
        return settings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to reset settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset settings")

async def _delete_settings_impl(
    user_id: str,
    settings_service: SettingsService
):
    """Implementation for delete settings"""
    logger.info(f"🚀 API: Delete settings requested for user: {user_id}")
    
    try:
        success = await settings_service.delete_settings(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        logger.info(f"✅ API: Settings deleted successfully for user: {user_id}")
        return {"message": "Settings deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to delete settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete settings")

@router.delete(
    "/",
    summary="Delete user settings",
    description="Delete user settings"
)
async def delete_settings(
    user_id: str,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Delete user settings (without trailing slash)"""
    return await _delete_settings_impl(user_id, settings_service)

@router.delete(
    "",
    summary="Delete user settings",
    description="Delete user settings",
    include_in_schema=False
)
async def delete_settings_no_slash(
    user_id: str,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Delete user settings (with trailing slash)"""
    return await _delete_settings_impl(user_id, settings_service)

__all__ = ["router"]