"""
Bot Repository for Chat Marketplace Service
Handles Bot and BotCategory operations
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, and_, or_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from ._base_repository import AsyncBaseRepository
from ..model.sqlalchemy_models import Bot, BotCategory, Conversation
from ..model.dto.marketplace_dto import BotStatus

class BotCategoryRepository(AsyncBaseRepository[BotCategory]):
    """Repository for BotCategory operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, BotCategory)
    
    async def get_active_categories(self, limit: int = 100, offset: int = 0) -> List[BotCategory]:
        """Get active categories ordered by sort_order"""
        stmt = (
            select(BotCategory)
            .where(BotCategory.is_active == True)
            .order_by(asc(BotCategory.sort_order), asc(BotCategory.name))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_with_bot_count(self, category_id: str) -> Optional[Dict[str, Any]]:
        """Get category with bot count"""
        category_stmt = select(BotCategory).where(BotCategory.category_id == category_id)
        category_result = await self.session.execute(category_stmt)
        category = category_result.scalar_one_or_none()
        
        if not category:
            return None
        
        # Count active bots in this category
        bot_count_stmt = (
            select(func.count(Bot.bot_id))
            .where(Bot.category_id == category_id)
            .where(Bot.status == BotStatus.ACTIVE)
        )
        bot_count_result = await self.session.execute(bot_count_stmt)
        bot_count = bot_count_result.scalar() or 0
        
        return {
            "category": category,
            "bot_count": bot_count
        }
    
    async def get_categories_with_bots(self, limit: int = 50) -> List[BotCategory]:
        """Get categories that have active bots"""
        stmt = (
            select(BotCategory)
            .options(selectinload(BotCategory.bots.and_(Bot.status == BotStatus.ACTIVE)))
            .where(BotCategory.is_active == True)
            .order_by(asc(BotCategory.sort_order))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_name(self, name: str) -> Optional[BotCategory]:
        """Get category by name"""
        stmt = select(BotCategory).where(BotCategory.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def search_categories(self, query: str, limit: int = 20, offset: int = 0) -> List[BotCategory]:
        """Search categories by name or description"""
        stmt = (
            select(BotCategory)
            .where(
                and_(
                    BotCategory.is_active == True,
                    or_(
                        BotCategory.name.ilike(f"%{query}%"),
                        BotCategory.description.ilike(f"%{query}%")
                    )
                )
            )
            .order_by(asc(BotCategory.sort_order))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

class BotRepository(AsyncBaseRepository[Bot]):
    """Repository for Bot operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Bot)
    
    async def get_by_name(self, name: str) -> Optional[Bot]:
        """Get bot by unique name"""
        stmt = select(Bot).where(Bot.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_with_category(self, bot_id: str) -> Optional[Bot]:
        """Get bot with category information"""
        stmt = (
            select(Bot)
            .options(selectinload(Bot.category))
            .where(Bot.bot_id == bot_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_category(
        self, 
        category_id: str, 
        status: Optional[BotStatus] = None,
        limit: int = 20, 
        offset: int = 0
    ) -> List[Bot]:
        """Get bots by category"""
        stmt = select(Bot).where(Bot.category_id == category_id)
        
        if status:
            stmt = stmt.where(Bot.status == status)
        else:
            stmt = stmt.where(Bot.status == BotStatus.ACTIVE)
        
        stmt = (
            stmt.order_by(desc(Bot.is_featured), desc(Bot.rating), asc(Bot.display_name))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_featured_bots(self, limit: int = 10) -> List[Bot]:
        """Get featured bots"""
        stmt = (
            select(Bot)
            .where(Bot.is_featured == True)
            .where(Bot.status == BotStatus.ACTIVE)
            .order_by(desc(Bot.rating), asc(Bot.display_name))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_premium_bots(self, limit: int = 20, offset: int = 0) -> List[Bot]:
        """Get premium bots"""
        stmt = (
            select(Bot)
            .where(Bot.is_premium == True)
            .where(Bot.status == BotStatus.ACTIVE)
            .order_by(desc(Bot.rating), asc(Bot.display_name))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_top_rated_bots(self, limit: int = 10) -> List[Bot]:
        """Get top rated bots"""
        stmt = (
            select(Bot)
            .where(Bot.status == BotStatus.ACTIVE)
            .where(Bot.rating.isnot(None))
            .order_by(desc(Bot.rating), desc(Bot.total_conversations))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_most_used_bots(self, limit: int = 10) -> List[Bot]:
        """Get most used bots by conversation count"""
        stmt = (
            select(Bot)
            .where(Bot.status == BotStatus.ACTIVE)
            .order_by(desc(Bot.total_conversations), desc(Bot.rating))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def search_bots(
        self,
        query: str,
        category_id: Optional[str] = None,
        status: Optional[BotStatus] = None,
        is_featured: Optional[bool] = None,
        is_premium: Optional[bool] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "display_name",
        sort_order: str = "asc",
        limit: int = 20,
        offset: int = 0
    ) -> List[Bot]:
        """Search bots with advanced filters"""
        stmt = (
            select(Bot)
            .where(
                or_(
                    Bot.name.ilike(f"%{query}%"),
                    Bot.display_name.ilike(f"%{query}%"),
                    Bot.description.ilike(f"%{query}%")
                )
            )
        )
        
        # Apply filters
        if category_id:
            stmt = stmt.where(Bot.category_id == category_id)
        
        if status:
            stmt = stmt.where(Bot.status == status)
        else:
            stmt = stmt.where(Bot.status == BotStatus.ACTIVE)
        
        if is_featured is not None:
            stmt = stmt.where(Bot.is_featured == is_featured)
        
        if is_premium is not None:
            stmt = stmt.where(Bot.is_premium == is_premium)
        
        if min_rating is not None:
            stmt = stmt.where(Bot.rating >= min_rating)
        
        # Apply sorting
        sort_column = getattr(Bot, sort_by, Bot.display_name)
        if sort_order.lower() == "desc":
            stmt = stmt.order_by(desc(sort_column))
        else:
            stmt = stmt.order_by(asc(sort_column))
        
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_status(self, status: BotStatus, limit: int = 100, offset: int = 0) -> List[Bot]:
        """Get bots by status"""
        stmt = (
            select(Bot)
            .where(Bot.status == status)
            .order_by(desc(Bot.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_conversation_count(self, bot_id: str) -> bool:
        """Update bot's total conversation count"""
        # Count conversations for this bot
        count_stmt = (
            select(func.count(Conversation.conversation_id))
            .where(Conversation.bot_id == bot_id)
        )
        count_result = await self.session.execute(count_stmt)
        total_conversations = count_result.scalar() or 0
        
        # Update bot's conversation count
        update_stmt = (
            update(Bot)
            .where(Bot.bot_id == bot_id)
            .values(total_conversations=total_conversations)
        )
        result = await self.session.execute(update_stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def update_rating(self, bot_id: str, new_rating: float) -> bool:
        """Update bot's rating"""
        stmt = (
            update(Bot)
            .where(Bot.bot_id == bot_id)
            .values(rating=new_rating)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def update_status(self, bot_id: str, status: BotStatus) -> bool:
        """Update bot's status"""
        stmt = (
            update(Bot)
            .where(Bot.bot_id == bot_id)
            .values(status=status)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def count_by_status(self, status: BotStatus) -> int:
        """Count bots by status"""
        stmt = select(func.count(Bot.bot_id)).where(Bot.status == status)
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def count_by_category(self, category_id: str, status: Optional[BotStatus] = None) -> int:
        """Count bots by category"""
        stmt = select(func.count(Bot.bot_id)).where(Bot.category_id == category_id)
        
        if status:
            stmt = stmt.where(Bot.status == status)
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def get_bot_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        total_stmt = select(func.count(Bot.bot_id))
        active_stmt = select(func.count(Bot.bot_id)).where(Bot.status == BotStatus.ACTIVE)
        pending_stmt = select(func.count(Bot.bot_id)).where(Bot.status == BotStatus.PENDING)
        featured_stmt = (
            select(func.count(Bot.bot_id))
            .where(Bot.is_featured == True)
            .where(Bot.status == BotStatus.ACTIVE)
        )
        premium_stmt = (
            select(func.count(Bot.bot_id))
            .where(Bot.is_premium == True)
            .where(Bot.status == BotStatus.ACTIVE)
        )
        
        total_result = await self.session.execute(total_stmt)
        active_result = await self.session.execute(active_stmt)
        pending_result = await self.session.execute(pending_stmt)
        featured_result = await self.session.execute(featured_stmt)
        premium_result = await self.session.execute(premium_stmt)
        
        # Get bots by category
        category_stats_stmt = (
            select(BotCategory.name, func.count(Bot.bot_id))
            .outerjoin(Bot, BotCategory.category_id == Bot.category_id)
            .where(or_(Bot.status == BotStatus.ACTIVE, Bot.status.is_(None)))
            .group_by(BotCategory.category_id, BotCategory.name)
        )
        category_stats_result = await self.session.execute(category_stats_stmt)
        bots_by_category = {row[0]: row[1] for row in category_stats_result}
        
        return {
            "total_bots": total_result.scalar() or 0,
            "active_bots": active_result.scalar() or 0,
            "pending_bots": pending_result.scalar() or 0,
            "featured_bots": featured_result.scalar() or 0,
            "premium_bots": premium_result.scalar() or 0,
            "bots_by_category": bots_by_category,
        }

__all__ = [
    "BotCategoryRepository",
    "BotRepository"
]