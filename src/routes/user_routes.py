"""
User Routes for Chat Marketplace Service
Handles user authentication and management endpoints
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from datalayer.database import get_postgres_session
from sqlalchemy.ext.asyncio import AsyncSession
from services.user_service import UserService
from datalayer.model.dto.auth_dto import (
    UserCreateDto, UserUpdateDto, UserResponseDto, UserWithProfileDto,
    LoginDto, TokenResponseDto, PasswordChangeDto, PasswordResetRequestDto,
    PasswordResetDto, UserListResponseDto, UserStatus
)

logger = logging.getLogger(__name__)

# Router configuration
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}}
)

# Dependency functions
def get_user_service(session: AsyncSession = Depends(get_postgres_session)) -> UserService:
    """User service dependency"""
    return UserService(session)

@router.post(
    "/register",
    response_model=UserResponseDto,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account with email and password"
)
async def register_user(
    user_data: UserCreateDto,
    user_service: UserService = Depends(get_user_service)
):
    """Register a new user"""
    logger.info(f"🚀 API: User registration requested for: {user_data.email}")
    
    try:
        user = await user_service.create_user(user_data)
        logger.info(f"✅ API: User registered successfully: {user.user_id}")
        return user
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Registration validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ API: User registration failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to register user")

@router.post(
    "/login",
    response_model=UserResponseDto,
    summary="User login",
    description="Authenticate user with email and password"
)
async def login_user(
    login_data: LoginDto,
    user_service: UserService = Depends(get_user_service)
):
    """Authenticate user"""
    logger.info(f"🚀 API: Login requested for: {login_data.email}")
    
    try:
        user = await user_service.authenticate_user(login_data)
        if not user:
            logger.warning(f"⚠️ API: Invalid credentials for: {login_data.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        logger.info(f"✅ API: User authenticated successfully: {user.user_id}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Authentication failed: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@router.get(
    "/me",
    response_model=UserWithProfileDto,
    summary="Get current user",
    description="Get current user information with profile and settings"
)
async def get_current_user(
    user_id: str = Query(..., description="Current user ID"),
    user_service: UserService = Depends(get_user_service)
):
    """Get current user information"""
    logger.info(f"🚀 API: Get current user requested: {user_id}")
    
    try:
        user = await user_service.get_user_by_id(user_id, include_profile=True)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"✅ API: Current user retrieved: {user_id}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to get current user: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user information")

@router.get(
    "/stats",
    summary="Get user statistics",
    description="Get user statistics and metrics"
)
async def get_user_stats(
    user_service: UserService = Depends(get_user_service)
):
    """Get user statistics"""
    logger.info("🚀 API: Get user stats requested")
    
    try:
        stats = await user_service.get_user_stats()
        logger.info("✅ API: User stats retrieved")
        return stats
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get user stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user statistics")

@router.get(
    "/{user_id}",
    response_model=UserResponseDto,
    summary="Get user by ID",
    description="Get user information by user ID"
)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID"""
    logger.info(f"🚀 API: Get user requested: {user_id}")
    
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"✅ API: User retrieved: {user_id}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to get user: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")

@router.put(
    "/{user_id}",
    response_model=UserResponseDto,
    summary="Update user",
    description="Update user information"
)
async def update_user(
    user_id: str,
    update_data: UserUpdateDto,
    user_service: UserService = Depends(get_user_service)
):
    """Update user information"""
    logger.info(f"🚀 API: Update user requested: {user_id}")
    
    try:
        user = await user_service.update_user(user_id, update_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"✅ API: User updated successfully: {user_id}")
        return user
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Update validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to update user: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")

@router.post(
    "/{user_id}/change-password",
    summary="Change password",
    description="Change user password"
)
async def change_password(
    user_id: str,
    password_data: PasswordChangeDto,
    user_service: UserService = Depends(get_user_service)
):
    """Change user password"""
    logger.info(f"🚀 API: Change password requested: {user_id}")
    
    try:
        success = await user_service.change_password(user_id, password_data)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid current password or user not found")
        
        logger.info(f"✅ API: Password changed successfully: {user_id}")
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to change password: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")

@router.post(
    "/{user_id}/verify-email",
    summary="Verify email",
    description="Mark user email as verified"
)
async def verify_email(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """Verify user email"""
    logger.info(f"🚀 API: Verify email requested: {user_id}")
    
    try:
        success = await user_service.verify_user_email(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"✅ API: Email verified successfully: {user_id}")
        return {"message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to verify email: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify email")

@router.post(
    "/{user_id}/deactivate",
    summary="Deactivate user",
    description="Deactivate user account"
)
async def deactivate_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """Deactivate user account"""
    logger.info(f"🚀 API: Deactivate user requested: {user_id}")
    
    try:
        success = await user_service.deactivate_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"✅ API: User deactivated successfully: {user_id}")
        return {"message": "User deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to deactivate user: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate user")

@router.get(
    "/",
    response_model=UserListResponseDto,
    summary="Search users",
    description="Search users with filters and pagination"
)
async def search_users(
    query: Optional[str] = Query(None, description="Search query"),
    status: Optional[UserStatus] = Query(None, description="User status filter"),
    limit: int = Query(20, ge=1, le=200, description="Number of users to return"),
    offset: int = Query(0, ge=0, description="Number of users to skip"),
    user_service: UserService = Depends(get_user_service)
):
    """Search users"""
    logger.info(f"🚀 API: Search users requested: query='{query}', status={status}")
    
    try:
        if query:
            result = await user_service.search_users(query, status, limit, offset)
        else:
            # If no query, get users by status
            users = await user_service.get_users_by_status(status or UserStatus.ACTIVE, limit, offset)
            # Create paginated response
            has_next = len(users) == limit  # Simple estimation
            has_prev = offset > 0
            
            result = UserListResponseDto(
                users=users,
                total=len(users) + offset,
                page=(offset // limit) + 1,
                limit=limit,
                has_next=has_next,
                has_prev=has_prev
            )
        
        logger.info(f"✅ API: Users search completed: {len(result.users)} users found")
        return result
        
    except Exception as e:
        logger.error(f"❌ API: Failed to search users: {e}")
        raise HTTPException(status_code=500, detail="Failed to search users")


__all__ = ["router"]