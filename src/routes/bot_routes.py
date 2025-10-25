"""
Bot Routes for Chat Marketplace Service
Handles bot marketplace and bot category endpoints
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from datalayer.database import get_postgres_session
from sqlalchemy.ext.asyncio import AsyncSession
from services.bot_service import BotService
from datalayer.model.dto.marketplace_dto import (
    BotCreateDto, BotUpdateDto, BotResponseDto, BotWithCategoryDto,
    BotListResponseDto, BotDetailDto, BotStatus, BotSearchDto, BotStatsDto,
    BotCategoryCreateDto, BotCategoryUpdateDto, BotCategoryResponseDto,
    BotCategoryWithBotsDto, BotCategoryListResponseDto, CategorySearchDto,
    CategoryStatsDto
)

logger = logging.getLogger(__name__)

# Bot Categories Router
categories_router = APIRouter(
    prefix="/marketplace/bot-categories",
    tags=["Bot Categories"],
    responses={404: {"description": "Not found"}}
)

# Bots Router
bots_router = APIRouter(
    prefix="/marketplace/bots",
    tags=["Bots"],
    responses={404: {"description": "Not found"}}
)

# Dependency functions
def get_bot_service(session: AsyncSession = Depends(get_postgres_session)) -> BotService:
    """Bot service dependency"""
    return BotService(session)

# Bot Category Endpoints
@categories_router.post(
    "/",
    response_model=BotCategoryResponseDto,
    status_code=status.HTTP_201_CREATED,
    summary="Create bot category",
    description="Create a new bot category (admin only)"
)
async def create_category(
    category_data: BotCategoryCreateDto,
    bot_service: BotService = Depends(get_bot_service)
):
    """Create bot category"""
    logger.info(f"🚀 API: Create category requested: {category_data.name}")
    
    try:
        category = await bot_service.create_category(category_data)
        logger.info(f"✅ API: Category created successfully: {category.category_id}")
        return category
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Category creation validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ API: Category creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create category: {str(e)}")

@categories_router.get(
    "/",
    response_model=List[BotCategoryResponseDto],
    summary="Get active categories",
    description="Get all active bot categories"
)
async def get_active_categories(
    limit: int = Query(100, ge=1, le=200, description="Number of categories to return"),
    offset: int = Query(0, ge=0, description="Number of categories to skip"),
    bot_service: BotService = Depends(get_bot_service)
):
    """Get active categories"""
    logger.info("🚀 API: Get active categories requested")
    
    try:
        categories = await bot_service.get_active_categories(limit, offset)
        logger.info(f"✅ API: Active categories retrieved: {len(categories)} categories")
        return categories
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get active categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active categories")

@categories_router.get(
    "/{category_id}",
    response_model=BotCategoryResponseDto,
    summary="Get category",
    description="Get bot category by ID"
)
async def get_category(
    category_id: str,
    bot_service: BotService = Depends(get_bot_service)
):
    """Get category by ID"""
    logger.info(f"🚀 API: Get category requested: {category_id}")
    
    try:
        category = await bot_service.get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        logger.info(f"✅ API: Category retrieved: {category_id}")
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to get category: {e}")
        raise HTTPException(status_code=500, detail="Failed to get category")

@categories_router.get(
    "/search",
    response_model=BotCategoryListResponseDto,
    summary="Search categories",
    description="Search bot categories with filters"
)
async def search_categories(
    query: Optional[str] = Query(None, description="Search query"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    has_bots: Optional[bool] = Query(None, description="Filter categories that have bots"),
    sort_by: Optional[str] = Query("sort_order", description="Sort field"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc, desc"),
    limit: int = Query(20, ge=1, le=200, description="Number of categories to return"),
    offset: int = Query(0, ge=0, description="Number of categories to skip"),
    bot_service: BotService = Depends(get_bot_service)
):
    """Search categories"""
    logger.info(f"🚀 API: Search categories requested: query='{query}'")
    
    try:
        search_data = CategorySearchDto(
            query=query,
            is_active=is_active,
            has_bots=has_bots,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )
        
        categories = await bot_service.search_categories(search_data)
        logger.info(f"✅ API: Category search completed: {len(categories.categories)} categories found")
        return categories
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Search validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ API: Failed to search categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to search categories")

# Bot Endpoints
@bots_router.post(
    "/",
    response_model=BotResponseDto,
    status_code=status.HTTP_201_CREATED,
    summary="Create bot",
    description="Create a new bot"
)
async def create_bot(
    bot_data: BotCreateDto,
    created_by: Optional[str] = Query(None, description="Creator user ID"),
    bot_service: BotService = Depends(get_bot_service)
):
    """Create bot"""
    logger.info(f"🚀 API: Create bot requested: {bot_data.name}")
    
    try:
        bot = await bot_service.create_bot(bot_data, created_by)
        logger.info(f"✅ API: Bot created successfully: {bot.bot_id}")
        return bot
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Bot creation validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ API: Bot creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create bot")

@bots_router.get(
    "/",
    response_model=BotListResponseDto,
    summary="Search bots",
    description="Search bots with advanced filters"
)
async def search_bots(
    query: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[BotStatus] = Query(None, description="Filter by status"),
    is_featured: Optional[bool] = Query(None, description="Filter featured bots"),
    is_premium: Optional[bool] = Query(None, description="Filter premium bots"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    sort_by: Optional[str] = Query("name", description="Sort field"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc, desc"),
    limit: int = Query(20, ge=1, le=200, description="Number of bots to return"),
    offset: int = Query(0, ge=0, description="Number of bots to skip"),
    bot_service: BotService = Depends(get_bot_service)
):
    """Search bots"""
    logger.info(f"🚀 API: Search bots requested: query='{query}'")
    
    try:
        search_data = BotSearchDto(
            query=query,
            category_id=category_id,
            status=status,
            is_featured=is_featured,
            is_premium=is_premium,
            min_rating=min_rating,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )
        
        bots = await bot_service.search_bots(search_data)
        logger.info(f"✅ API: Bot search completed: {len(bots.bots)} bots found")
        return bots
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Search validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ API: Failed to search bots: {e}")
        raise HTTPException(status_code=500, detail="Failed to search bots")

@bots_router.get(
    "/{bot_id}",
    response_model=BotDetailDto,
    summary="Get bot detail",
    description="Get detailed bot information by ID"
)
async def get_bot_detail(
    bot_id: str,
    bot_service: BotService = Depends(get_bot_service)
):
    """Get bot detail"""
    logger.info(f"🚀 API: Get bot detail requested: {bot_id}")
    
    try:
        bot = await bot_service.get_bot_detail(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        logger.info(f"✅ API: Bot detail retrieved: {bot_id}")
        return bot
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to get bot detail: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bot detail")

@bots_router.get(
    "/name/{bot_name}",
    response_model=BotResponseDto,
    summary="Get bot by name",
    description="Get bot information by unique name"
)
async def get_bot_by_name(
    bot_name: str,
    bot_service: BotService = Depends(get_bot_service)
):
    """Get bot by name"""
    logger.info(f"🚀 API: Get bot by name requested: {bot_name}")
    
    try:
        bot = await bot_service.get_bot_by_name(bot_name)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        logger.info(f"✅ API: Bot retrieved by name: {bot_name}")
        return bot
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to get bot by name: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bot by name")

@bots_router.put(
    "/{bot_id}",
    response_model=BotResponseDto,
    summary="Update bot",
    description="Update bot information"
)
async def update_bot(
    bot_id: str,
    update_data: BotUpdateDto,
    bot_service: BotService = Depends(get_bot_service)
):
    """Update bot"""
    logger.info(f"🚀 API: Update bot requested: {bot_id}")
    
    try:
        bot = await bot_service.update_bot(bot_id, update_data)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        logger.info(f"✅ API: Bot updated successfully: {bot_id}")
        return bot
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Bot update validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to update bot: {e}")
        raise HTTPException(status_code=500, detail="Failed to update bot")

@bots_router.get(
    "/category/{category_id}",
    response_model=BotListResponseDto,
    summary="Get bots by category",
    description="Get bots in a specific category"
)
async def get_bots_by_category(
    category_id: str,
    status: Optional[BotStatus] = Query(BotStatus.ACTIVE, description="Filter by bot status"),
    limit: int = Query(20, ge=1, le=200, description="Number of bots to return"),
    offset: int = Query(0, ge=0, description="Number of bots to skip"),
    bot_service: BotService = Depends(get_bot_service)
):
    """Get bots by category"""
    logger.info(f"🚀 API: Get bots by category requested: {category_id}")
    
    try:
        bots = await bot_service.get_bots_by_category(category_id, status, limit, offset)
        logger.info(f"✅ API: Bots by category retrieved: {len(bots.bots)} bots")
        return bots
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get bots by category: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bots by category")

@bots_router.get(
    "/featured",
    response_model=List[BotResponseDto],
    summary="Get featured bots",
    description="Get featured bots"
)
async def get_featured_bots(
    limit: int = Query(10, ge=1, le=50, description="Number of bots to return"),
    bot_service: BotService = Depends(get_bot_service)
):
    """Get featured bots"""
    logger.info("🚀 API: Get featured bots requested")
    
    try:
        bots = await bot_service.get_featured_bots(limit)
        logger.info(f"✅ API: Featured bots retrieved: {len(bots)} bots")
        return bots
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get featured bots: {e}")
        raise HTTPException(status_code=500, detail="Failed to get featured bots")

@bots_router.get(
    "/top-rated",
    response_model=List[BotResponseDto],
    summary="Get top rated bots",
    description="Get top rated bots"
)
async def get_top_rated_bots(
    limit: int = Query(10, ge=1, le=50, description="Number of bots to return"),
    bot_service: BotService = Depends(get_bot_service)
):
    """Get top rated bots"""
    logger.info("🚀 API: Get top rated bots requested")
    
    try:
        bots = await bot_service.get_top_rated_bots(limit)
        logger.info(f"✅ API: Top rated bots retrieved: {len(bots)} bots")
        return bots
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get top rated bots: {e}")
        raise HTTPException(status_code=500, detail="Failed to get top rated bots")

@bots_router.get(
    "/most-used",
    response_model=List[BotResponseDto],
    summary="Get most used bots",
    description="Get most used bots by conversation count"
)
async def get_most_used_bots(
    limit: int = Query(10, ge=1, le=50, description="Number of bots to return"),
    bot_service: BotService = Depends(get_bot_service)
):
    """Get most used bots"""
    logger.info("🚀 API: Get most used bots requested")
    
    try:
        bots = await bot_service.get_most_used_bots(limit)
        logger.info(f"✅ API: Most used bots retrieved: {len(bots)} bots")
        return bots
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get most used bots: {e}")
        raise HTTPException(status_code=500, detail="Failed to get most used bots")

@bots_router.post(
    "/{bot_id}/approve",
    summary="Approve bot",
    description="Approve a pending bot (admin only)"
)
async def approve_bot(
    bot_id: str,
    bot_service: BotService = Depends(get_bot_service)
):
    """Approve bot"""
    logger.info(f"🚀 API: Approve bot requested: {bot_id}")
    
    try:
        success = await bot_service.approve_bot(bot_id)
        if not success:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        logger.info(f"✅ API: Bot approved successfully: {bot_id}")
        return {"message": "Bot approved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to approve bot: {e}")
        raise HTTPException(status_code=500, detail="Failed to approve bot")

@bots_router.post(
    "/{bot_id}/reject",
    summary="Reject bot",
    description="Reject a pending bot (admin only)"
)
async def reject_bot(
    bot_id: str,
    bot_service: BotService = Depends(get_bot_service)
):
    """Reject bot"""
    logger.info(f"🚀 API: Reject bot requested: {bot_id}")
    
    try:
        success = await bot_service.reject_bot(bot_id)
        if not success:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        logger.info(f"✅ API: Bot rejected successfully: {bot_id}")
        return {"message": "Bot rejected successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to reject bot: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject bot")

@bots_router.patch(
    "/{bot_id}/rating",
    summary="Update bot rating",
    description="Update bot rating"
)
async def update_bot_rating(
    bot_id: str,
    rating: float = Query(..., ge=0, le=5, description="New rating (0-5)"),
    bot_service: BotService = Depends(get_bot_service)
):
    """Update bot rating"""
    logger.info(f"🚀 API: Update bot rating requested: {bot_id}")
    
    try:
        success = await bot_service.update_bot_rating(bot_id, rating)
        if not success:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        logger.info(f"✅ API: Bot rating updated successfully: {bot_id}")
        return {"message": "Bot rating updated successfully", "rating": rating}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to update bot rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to update bot rating")

@bots_router.get(
    "/stats",
    response_model=BotStatsDto,
    summary="Get bot statistics",
    description="Get comprehensive bot marketplace statistics"
)
async def get_bot_stats(
    bot_service: BotService = Depends(get_bot_service)
):
    """Get bot statistics"""
    logger.info("🚀 API: Get bot stats requested")
    
    try:
        stats = await bot_service.get_bot_stats()
        logger.info("✅ API: Bot stats retrieved")
        return stats
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get bot stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bot statistics")

__all__ = ["categories_router", "bots_router"]