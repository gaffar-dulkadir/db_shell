"""
Bot Service for Chat Marketplace Service
Handles bot and bot category operations
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from datalayer.repository.bot_repository import BotRepository, BotCategoryRepository
from datalayer.model.sqlalchemy_models import Bot, BotCategory
from datalayer.model.dto.marketplace_dto import (
    BotCreateDto, BotUpdateDto, BotResponseDto, BotWithCategoryDto,
    BotListResponseDto, BotDetailDto, BotStatus, BotSearchDto, BotStatsDto,
    BotCategoryCreateDto, BotCategoryUpdateDto, BotCategoryResponseDto,
    BotCategoryWithBotsDto, BotCategoryListResponseDto, CategorySearchDto,
    CategoryStatsDto
)

logger = logging.getLogger(__name__)

class BotService:
    """Service for bot operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.bot_repo = BotRepository(session)
        self.category_repo = BotCategoryRepository(session)
        logger.debug("✅ BotService initialized")
    
    async def create_bot(self, bot_data: BotCreateDto, created_by: Optional[str] = None) -> BotResponseDto:
        """Create a new bot"""
        logger.info(f"📝 Creating bot: {bot_data.name}")
        
        try:
            # Validate category exists
            category = await self.category_repo.get_by_id(bot_data.category_id)
            if not category:
                raise ValueError(f"Category {bot_data.category_id} not found")
            
            # Check if bot name already exists
            existing_bot = await self.bot_repo.get_by_name(bot_data.name)
            if existing_bot:
                raise ValueError(f"Bot with name {bot_data.name} already exists")
            
            # Create bot
            bot = Bot(
                category_id=bot_data.category_id,
                name=bot_data.name,
                display_name=bot_data.display_name,
                description=bot_data.description,
                avatar_url=bot_data.avatar_url,
                is_featured=bot_data.is_featured,
                is_premium=bot_data.is_premium,
                capabilities=bot_data.capabilities,
                configuration=bot_data.configuration,
                created_by=created_by,
                status=BotStatus.PENDING  # New bots start as pending
            )
            
            saved_bot = await self.bot_repo.save(bot)
            await self.session.commit()
            
            logger.info(f"✅ Bot created successfully: {saved_bot.bot_id}")
            return self._bot_to_dto(saved_bot)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to create bot: {e}")
            raise
    
    async def get_bot_by_id(self, bot_id: str, include_category: bool = False) -> Optional[BotResponseDto]:
        """Get bot by ID"""
        logger.debug(f"🔍 Getting bot: {bot_id}")
        
        try:
            if include_category:
                bot = await self.bot_repo.get_with_category(bot_id)
                if bot:
                    return self._bot_with_category_to_dto(bot)
            else:
                bot = await self.bot_repo.get_by_id(bot_id)
                if bot:
                    return self._bot_to_dto(bot)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get bot: {e}")
            raise
    
    async def get_bot_by_name(self, name: str) -> Optional[BotResponseDto]:
        """Get bot by name"""
        logger.debug(f"🔍 Getting bot by name: {name}")
        
        try:
            bot = await self.bot_repo.get_by_name(name)
            return self._bot_to_dto(bot) if bot else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get bot by name: {e}")
            raise
    
    async def get_bot_detail(self, bot_id: str) -> Optional[BotDetailDto]:
        """Get detailed bot information"""
        logger.debug(f"🔍 Getting bot detail: {bot_id}")
        
        try:
            bot = await self.bot_repo.get_with_category(bot_id)
            if not bot:
                return None
            
            # Get conversation count for this bot
            conversation_count = await self.bot_repo.count_by_bot(bot_id)
            
            bot_dto = self._bot_to_dto(bot)
            category_dto = self._category_to_dto(bot.category) if bot.category else None
            
            return BotDetailDto(
                **bot_dto.dict(),
                category=category_dto,
                conversation_count=conversation_count,
                recent_conversations=0  # Could be enhanced to show recent activity
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get bot detail: {e}")
            raise
    
    async def update_bot(self, bot_id: str, update_data: BotUpdateDto) -> Optional[BotResponseDto]:
        """Update bot"""
        logger.info(f"📝 Updating bot: {bot_id}")
        
        try:
            bot = await self.bot_repo.get_by_id(bot_id)
            if not bot:
                return None
            
            # Validate category if changing
            if update_data.category_id and update_data.category_id != bot.category_id:
                category = await self.category_repo.get_by_id(update_data.category_id)
                if not category:
                    raise ValueError(f"Category {update_data.category_id} not found")
            
            # Update fields
            if update_data.category_id is not None:
                bot.category_id = update_data.category_id
            if update_data.display_name is not None:
                bot.display_name = update_data.display_name
            if update_data.description is not None:
                bot.description = update_data.description
            if update_data.avatar_url is not None:
                bot.avatar_url = update_data.avatar_url
            if update_data.status is not None:
                bot.status = update_data.status
            if update_data.is_featured is not None:
                bot.is_featured = update_data.is_featured
            if update_data.is_premium is not None:
                bot.is_premium = update_data.is_premium
            if update_data.capabilities is not None:
                bot.capabilities = update_data.capabilities
            if update_data.configuration is not None:
                bot.configuration = update_data.configuration
            
            bot.updated_at = datetime.utcnow()
            
            updated_bot = await self.bot_repo.save(bot)
            await self.session.commit()
            
            logger.info(f"✅ Bot updated successfully: {bot_id}")
            return self._bot_to_dto(updated_bot)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to update bot: {e}")
            raise
    
    async def search_bots(self, search_data: BotSearchDto) -> BotListResponseDto:
        """Search bots"""
        logger.debug(f"🔍 Searching bots: {search_data.query}")
        
        try:
            bots = await self.bot_repo.search_bots(
                query=search_data.query or "",
                category_id=search_data.category_id,
                status=search_data.status,
                is_featured=search_data.is_featured,
                is_premium=search_data.is_premium,
                min_rating=search_data.min_rating,
                sort_by=search_data.sort_by,
                sort_order=search_data.sort_order,
                limit=search_data.limit + 1,
                offset=search_data.offset
            )
            
            # Check if there are more results
            has_next = len(bots) > search_data.limit
            if has_next:
                bots = bots[:search_data.limit]
            
            has_prev = search_data.offset > 0
            
            # Estimate total for search results
            total = len(bots) + search_data.offset
            if has_next:
                total += 1
            
            bot_dtos = [self._bot_to_dto(bot) for bot in bots]
            
            return BotListResponseDto(
                bots=bot_dtos,
                total=total,
                page=(search_data.offset // search_data.limit) + 1,
                limit=search_data.limit,
                has_next=has_next,
                has_prev=has_prev
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to search bots: {e}")
            raise
    
    async def get_bots_by_category(
        self, 
        category_id: str, 
        status: Optional[BotStatus] = None,
        limit: int = 20, 
        offset: int = 0
    ) -> BotListResponseDto:
        """Get bots by category"""
        logger.debug(f"🔍 Getting bots by category: {category_id}")
        
        try:
            bots = await self.bot_repo.get_by_category(category_id, status, limit + 1, offset)
            
            # Check if there are more results
            has_next = len(bots) > limit
            if has_next:
                bots = bots[:limit]
            
            has_prev = offset > 0
            
            # Get total count
            total = await self.bot_repo.count_by_category(category_id, status)
            
            bot_dtos = [self._bot_to_dto(bot) for bot in bots]
            
            return BotListResponseDto(
                bots=bot_dtos,
                total=total,
                page=(offset // limit) + 1,
                limit=limit,
                has_next=has_next,
                has_prev=has_prev
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get bots by category: {e}")
            raise
    
    async def get_featured_bots(self, limit: int = 10) -> List[BotResponseDto]:
        """Get featured bots"""
        logger.debug(f"🔍 Getting featured bots")
        
        try:
            bots = await self.bot_repo.get_featured_bots(limit)
            return [self._bot_to_dto(bot) for bot in bots]
            
        except Exception as e:
            logger.error(f"❌ Failed to get featured bots: {e}")
            raise
    
    async def get_top_rated_bots(self, limit: int = 10) -> List[BotResponseDto]:
        """Get top rated bots"""
        logger.debug(f"🔍 Getting top rated bots")
        
        try:
            bots = await self.bot_repo.get_top_rated_bots(limit)
            return [self._bot_to_dto(bot) for bot in bots]
            
        except Exception as e:
            logger.error(f"❌ Failed to get top rated bots: {e}")
            raise
    
    async def get_most_used_bots(self, limit: int = 10) -> List[BotResponseDto]:
        """Get most used bots"""
        logger.debug(f"🔍 Getting most used bots")
        
        try:
            bots = await self.bot_repo.get_most_used_bots(limit)
            return [self._bot_to_dto(bot) for bot in bots]
            
        except Exception as e:
            logger.error(f"❌ Failed to get most used bots: {e}")
            raise
    
    async def approve_bot(self, bot_id: str) -> bool:
        """Approve a pending bot"""
        logger.info(f"✅ Approving bot: {bot_id}")
        
        try:
            success = await self.bot_repo.update_status(bot_id, BotStatus.ACTIVE)
            
            if success:
                logger.info(f"✅ Bot approved successfully: {bot_id}")
            else:
                logger.warning(f"⚠️ Bot not found for approval: {bot_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to approve bot: {e}")
            raise
    
    async def reject_bot(self, bot_id: str) -> bool:
        """Reject a pending bot"""
        logger.info(f"❌ Rejecting bot: {bot_id}")
        
        try:
            success = await self.bot_repo.update_status(bot_id, BotStatus.REJECTED)
            
            if success:
                logger.info(f"✅ Bot rejected successfully: {bot_id}")
            else:
                logger.warning(f"⚠️ Bot not found for rejection: {bot_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to reject bot: {e}")
            raise
    
    async def update_bot_rating(self, bot_id: str, rating: float) -> bool:
        """Update bot rating"""
        logger.info(f"⭐ Updating bot rating: {bot_id} -> {rating}")
        
        try:
            success = await self.bot_repo.update_rating(bot_id, rating)
            
            if success:
                logger.info(f"✅ Bot rating updated successfully: {bot_id}")
            else:
                logger.warning(f"⚠️ Bot not found for rating update: {bot_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to update bot rating: {e}")
            raise
    
    async def get_bot_stats(self) -> BotStatsDto:
        """Get bot statistics"""
        logger.debug("📊 Getting bot statistics")
        
        try:
            stats = await self.bot_repo.get_bot_stats()
            
            # Get top rated and most used bots
            top_rated_bots = await self.get_top_rated_bots(5)
            most_used_bots = await self.get_most_used_bots(5)
            
            return BotStatsDto(
                total_bots=stats["total_bots"],
                active_bots=stats["active_bots"],
                pending_bots=stats["pending_bots"],
                featured_bots=stats["featured_bots"],
                premium_bots=stats["premium_bots"],
                bots_by_category=stats["bots_by_category"],
                top_rated_bots=top_rated_bots,
                most_used_bots=most_used_bots
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get bot stats: {e}")
            raise
    
    # Category operations
    async def create_category(self, category_data: BotCategoryCreateDto) -> BotCategoryResponseDto:
        """Create a new bot category"""
        logger.info(f"📝 Creating category: {category_data.name}")
        
        try:
            # Check if category name already exists
            existing_category = await self.category_repo.get_by_name(category_data.name)
            if existing_category:
                raise ValueError(f"Category with name {category_data.name} already exists")
            
            # Create category
            category = BotCategory()
            category.category_name = category_data.name
            category.category_description = category_data.description
            category.icon = category_data.icon
            category.color = category_data.color
            category.is_active = category_data.is_active
            category.sort_order = category_data.sort_order
            
            saved_category = await self.category_repo.save(category)
            await self.session.commit()
            
            logger.info(f"✅ Category created successfully: {saved_category.category_id}")
            return self._category_to_dto(saved_category)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to create category: {e}")
            raise
    
    async def get_category_by_id(self, category_id: str) -> Optional[BotCategoryResponseDto]:
        """Get category by ID"""
        logger.debug(f"🔍 Getting category: {category_id}")
        
        try:
            category = await self.category_repo.get_by_id(category_id)
            return self._category_to_dto(category) if category else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get category: {e}")
            raise
    
    async def get_active_categories(self, limit: int = 100, offset: int = 0) -> List[BotCategoryResponseDto]:
        """Get active categories"""
        logger.debug("🔍 Getting active categories")
        
        try:
            categories = await self.category_repo.get_active_categories(limit, offset)
            return [self._category_to_dto(category) for category in categories]
            
        except Exception as e:
            logger.error(f"❌ Failed to get active categories: {e}")
            raise
    
    async def search_categories(self, search_data: CategorySearchDto) -> BotCategoryListResponseDto:
        """Search categories"""
        logger.debug(f"🔍 Searching categories: {search_data.query}")
        
        try:
            categories = await self.category_repo.search_categories(
                search_data.query or "", search_data.limit + 1, search_data.offset
            )
            
            # Check if there are more results
            has_next = len(categories) > search_data.limit
            if has_next:
                categories = categories[:search_data.limit]
            
            has_prev = search_data.offset > 0
            
            # Estimate total for search results
            total = len(categories) + search_data.offset
            if has_next:
                total += 1
            
            category_dtos = [self._category_to_dto(category) for category in categories]
            
            return BotCategoryListResponseDto(
                categories=category_dtos,
                total=total,
                page=(search_data.offset // search_data.limit) + 1,
                limit=search_data.limit,
                has_next=has_next,
                has_prev=has_prev
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to search categories: {e}")
            raise
    
    @staticmethod
    def _bot_to_dto(bot: Bot) -> BotResponseDto:
        """Convert Bot model to BotResponseDto"""
        return BotResponseDto(
            bot_id=bot.bot_id,
            category_id=bot.category_id,
            name=bot.name,
            display_name=bot.display_name,
            description=bot.description,
            avatar_url=bot.avatar_url,
            status=bot.status,
            is_featured=bot.is_featured,
            is_premium=bot.is_premium,
            rating=bot.rating,
            total_conversations=bot.total_conversations,
            capabilities=bot.capabilities,
            configuration=bot.configuration,
            created_by=bot.created_by,
            created_at=bot.created_at,
            updated_at=bot.updated_at
        )
    
    def _bot_with_category_to_dto(self, bot: Bot) -> BotWithCategoryDto:
        """Convert Bot model with category to BotWithCategoryDto"""
        bot_dto = self._bot_to_dto(bot)
        category_dto = None
        
        if hasattr(bot, 'category') and bot.category:
            category_dto = self._category_to_dto(bot.category)
        
        return BotWithCategoryDto(
            **bot_dto.dict(),
            category=category_dto
        )
    
    @staticmethod
    @staticmethod
    def _category_to_dto(category: BotCategory) -> BotCategoryResponseDto:
        """Convert BotCategory model to BotCategoryResponseDto"""
        return BotCategoryResponseDto(
            category_id=category.category_id,
            name=category.category_name,
            description=category.category_description,
            icon=category.icon,
            color=category.color,
            is_active=category.is_active,
            sort_order=category.sort_order,
            bot_count=0,  # Avoid async call in static method
            created_at=category.created_at,
            updated_at=category.updated_at
        )
__all__ = ["BotService"]