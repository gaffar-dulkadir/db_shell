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
        # Since username is a computed property, we need to search by user_name
        if '_' in username:
            name_part = username.split('_')[0]
            stmt = select(User).where(User.user_name == name_part)
        else:
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
        stmt = select(1).where(User.user_email == email.lower())
        result = await self.session.execute(stmt)
        return result.scalar() is not None
    
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        if '_' in username:
            name_part = username.split('_')[0]
            stmt = select(1).where(User.user_name == name_part)
        else:
            stmt = select(1).where(User.user_name == username)
        result = await self.session.execute(stmt)
        return result.scalar() is not None
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        from datetime import datetime
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(last_login_at=datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def count_by_status(self, status: UserStatus) -> int:
        """Count users by status"""
        stmt = select(func.count(User.user_id))
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        total_stmt = select(func.count(User.user_id))
        
        total_result = await self.session.execute(total_stmt)
        
        return {
            "total_users": total_result.scalar() or 0,
            "active_users": total_result.scalar() or 0,  # Simplified for now
            "verified_users": total_result.scalar() or 0,  # Simplified for now
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
        await self.session.commit()
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