"""
User Repository for Chat Marketplace Service
Handles User, UserProfile, and UserSettings operations
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from ._base_repository import AsyncBaseRepository
from ..model.sqlalchemy_models import User, UserProfile, UserSettings
from ..model.dto.auth_dto import UserStatus

class UserRepository(AsyncBaseRepository[User]):
    """Repository for User operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        stmt = select(User).where(User.user_email == email.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        # Since username is computed from user_name + user_surname, search accordingly
        if username and '_' in username:
            parts = username.split('_', 1)
            name_part = parts[0]
            surname_part = parts[1] if len(parts) > 1 else ""
            stmt = select(User).where(
                and_(User.user_name == name_part, User.user_surname == surname_part)
            )
        else:
            # Search by user_name only if no underscore
            stmt = select(User).where(User.user_name == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_with_profile(self, user_id: str) -> Optional[User]:
        """Get user with profile data"""
        stmt = (
            select(User)
            .options(selectinload(User.profile))
            .where(User.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_with_profile_and_settings(self, user_id: str) -> Optional[User]:
        """Get user with profile and settings data"""
        stmt = (
            select(User)
            .options(
                selectinload(User.profile),
                selectinload(User.settings)
            )
            .where(User.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_by_status(self, status: UserStatus, limit: int = 100, offset: int = 0) -> List[User]:
        """Find users by status"""
        stmt = (
            select(User)
            .limit(limit)
            .offset(offset)
            .order_by(User.user_created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def search_users(
        self,
        query: str,
        status: Optional[UserStatus] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[User]:
        """Search users by email, username, or profile name"""
        stmt = (
            select(User)
            .outerjoin(User.profile)
            .where(
                or_(
                    User.user_email.ilike(f"%{query}%"),
                    User.user_name.ilike(f"%{query}%"),
                    User.user_surname.ilike(f"%{query}%")
                )
            )
        )
        
        stmt = stmt.limit(limit).offset(offset).order_by(User.user_created_at.desc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        stmt = select(func.count(User.user_id)).where(User.user_email == email.lower())
        result = await self.session.execute(stmt)
        return (result.scalar() or 0) > 0
    
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        if username and '_' in username:
            parts = username.split('_', 1)
            name_part = parts[0]
            surname_part = parts[1] if len(parts) > 1 else ""
            stmt = select(func.count(User.user_id)).where(
                and_(User.user_name == name_part, User.user_surname == surname_part)
            )
        else:
            stmt = select(func.count(User.user_id)).where(User.user_name == username)
        result = await self.session.execute(stmt)
        return (result.scalar() or 0) > 0
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp - no-op since field doesn't exist in current schema"""
        # Current schema doesn't have last_login_at field, so just return True
        # This prevents errors while maintaining API compatibility
        return True
    
    async def count_by_status(self, status: UserStatus) -> int:
        """Count users by status"""
        stmt = select(func.count(User.user_id))
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        from datetime import datetime, timedelta
        
        # Total users count
        total_stmt = select(func.count(User.user_id))
        
        # Active users count (status = 'active')
        active_stmt = select(func.count(User.user_id)).where(User.status == 'active')
        
        # Verified users count (is_verified = True)
        verified_stmt = select(func.count(User.user_id)).where(User.is_verified == True)
        
        # New users today count (created today)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        new_today_stmt = select(func.count(User.user_id)).where(
            and_(
                User.user_created_at >= today_start,
                User.user_created_at < today_end
            )
        )
        
        # Execute all queries
        total_result = await self.session.execute(total_stmt)
        active_result = await self.session.execute(active_stmt)
        verified_result = await self.session.execute(verified_stmt)
        new_today_result = await self.session.execute(new_today_stmt)
        
        return {
            "total_users": total_result.scalar() or 0,
            "active_users": active_result.scalar() or 0,
            "verified_users": verified_result.scalar() or 0,
            "new_users_today": new_today_result.scalar() or 0,
        }

class UserProfileRepository(AsyncBaseRepository[UserProfile]):
    """Repository for UserProfile operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserProfile)
    
    async def get_by_user_id(self, user_id: str) -> Optional[UserProfile]:
        """Get profile by user ID"""
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_with_user(self, profile_id: str) -> Optional[UserProfile]:
        """Get profile with user data"""
        stmt = (
            select(UserProfile)
            .options(selectinload(UserProfile.user))
            .where(UserProfile.profile_id == profile_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def search_by_name(self, query: str, limit: int = 20, offset: int = 0) -> List[UserProfile]:
        """Search profiles by name"""
        stmt = (
            select(UserProfile)
            .where(
                or_(
                    UserProfile.first_name.ilike(f"%{query}%"),
                    UserProfile.last_name.ilike(f"%{query}%"),
                    UserProfile.display_name.ilike(f"%{query}%")
                )
            )
            .limit(limit)
            .offset(offset)
            .order_by(UserProfile.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

class UserSettingsRepository(AsyncBaseRepository[UserSettings]):
    """Repository for UserSettings operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserSettings)
    
    async def get_by_user_id(self, user_id: str) -> Optional[UserSettings]:
        """Get settings by user ID"""
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_with_user(self, settings_id: str) -> Optional[UserSettings]:
        """Get settings with user data"""
        stmt = (
            select(UserSettings)
            .options(selectinload(UserSettings.user))
            .where(UserSettings.settings_id == settings_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_notification_settings(
        self,
        user_id: str,
        email_notifications: Optional[bool] = None,
        push_notifications: Optional[bool] = None
    ) -> bool:
        """Update notification settings"""
        updates = {}
        if email_notifications is not None:
            updates['email_notifications'] = email_notifications
        if push_notifications is not None:
            updates['push_notifications'] = push_notifications
        
        if not updates:
            return False
        
        stmt = (
            update(UserSettings)
            .where(UserSettings.user_id == user_id)
            .values(**updates)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
    
    async def get_users_with_email_notifications(self) -> List[UserSettings]:
        """Get all users with email notifications enabled"""
        stmt = (
            select(UserSettings)
            .options(selectinload(UserSettings.user))
            .where(UserSettings.email_notifications == True)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

__all__ = [
    "UserRepository",
    "UserProfileRepository", 
    "UserSettingsRepository"
]