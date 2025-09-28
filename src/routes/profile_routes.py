"""
Profile Routes for Chat Marketplace Service
Handles user profile management endpoints
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from datalayer.database import get_postgres_session
from sqlalchemy.ext.asyncio import AsyncSession
from services.profile_service import ProfileService
from datalayer.model.dto.auth_dto import (
    UserProfileCreateDto, UserProfileUpdateDto, UserProfileResponseDto
)

logger = logging.getLogger(__name__)

# Router configuration
router = APIRouter(
    prefix="/users/{user_id}/profile",
    tags=["User Profiles"],
    responses={404: {"description": "Not found"}}
)

# Dependency functions
def get_profile_service(session: AsyncSession = Depends(get_postgres_session)) -> ProfileService:
    """Profile service dependency"""
    return ProfileService(session)

@router.post(
    "/",
    response_model=UserProfileResponseDto,
    status_code=status.HTTP_201_CREATED,
    summary="Create user profile",
    description="Create a new user profile"
)
async def create_profile(
    user_id: str,
    profile_data: UserProfileCreateDto,
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Create user profile"""
    logger.info(f"🚀 API: Create profile requested for user: {user_id}")
    
    try:
        profile = await profile_service.create_profile(user_id, profile_data)
        logger.info(f"✅ API: Profile created successfully: {profile.profile_id}")
        return profile
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Profile creation validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ API: Profile creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create profile")

@router.get(
    "/",
    response_model=UserProfileResponseDto,
    summary="Get user profile",
    description="Get user profile information"
)
async def get_profile(
    user_id: str,
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get user profile"""
    logger.info(f"🚀 API: Get profile requested for user: {user_id}")
    
    try:
        profile = await profile_service.get_profile_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        logger.info(f"✅ API: Profile retrieved: {profile.profile_id}")
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to get profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get profile")

@router.put(
    "/",
    response_model=UserProfileResponseDto,
    summary="Update user profile",
    description="Update user profile information"
)
async def update_profile(
    user_id: str,
    update_data: UserProfileUpdateDto,
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update user profile"""
    logger.info(f"🚀 API: Update profile requested for user: {user_id}")
    
    try:
        profile = await profile_service.update_profile(user_id, update_data)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        logger.info(f"✅ API: Profile updated successfully: {profile.profile_id}")
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to update profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

@router.patch(
    "/avatar",
    response_model=UserProfileResponseDto,
    summary="Update user avatar",
    description="Update user avatar URL"
)
async def update_avatar(
    user_id: str,
    avatar_url: str = Query(..., description="New avatar URL"),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update user avatar"""
    logger.info(f"🚀 API: Update avatar requested for user: {user_id}")
    
    try:
        profile = await profile_service.update_avatar(user_id, avatar_url)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        logger.info(f"✅ API: Avatar updated successfully for user: {user_id}")
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to update avatar: {e}")
        raise HTTPException(status_code=500, detail="Failed to update avatar")

@router.delete(
    "/",
    summary="Delete user profile",
    description="Delete user profile"
)
async def delete_profile(
    user_id: str,
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Delete user profile"""
    logger.info(f"🚀 API: Delete profile requested for user: {user_id}")
    
    try:
        success = await profile_service.delete_profile(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        logger.info(f"✅ API: Profile deleted successfully for user: {user_id}")
        return {"message": "Profile deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to delete profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete profile")

# Search profiles endpoint (without user_id prefix)
search_router = APIRouter(
    prefix="/profiles",
    tags=["User Profiles"],
    responses={404: {"description": "Not found"}}
)

@search_router.get(
    "/search",
    response_model=List[UserProfileResponseDto],
    summary="Search profiles",
    description="Search user profiles by name"
)
async def search_profiles(
    query: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=200, description="Number of profiles to return"),
    offset: int = Query(0, ge=0, description="Number of profiles to skip"),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Search user profiles"""
    logger.info(f"🚀 API: Search profiles requested: query='{query}'")
    
    try:
        profiles = await profile_service.search_profiles(query, limit, offset)
        logger.info(f"✅ API: Profiles search completed: {len(profiles)} profiles found")
        return profiles
        
    except Exception as e:
        logger.error(f"❌ API: Failed to search profiles: {e}")
        raise HTTPException(status_code=500, detail="Failed to search profiles")

__all__ = ["router", "search_router"]