"""
Conversation Routes for Chat Marketplace Service
Handles conversation management endpoints
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from datalayer.database import get_postgres_session
from sqlalchemy.ext.asyncio import AsyncSession
from services.conversation_service import ConversationService
from datalayer.model.dto.chat_dto import (
    ConversationCreateDto, ConversationUpdateDto, ConversationResponseDto,
    ConversationWithMessagesDto, ConversationListResponseDto, ConversationStatus,
    ConversationSearchDto, ConversationStatsDto
)

logger = logging.getLogger(__name__)

# Router configuration
router = APIRouter(
    prefix="/users/{user_id}/conversations",
    tags=["Conversations"],
    responses={404: {"description": "Not found"}}
)

# Dependency functions
def get_conversation_service(session: AsyncSession = Depends(get_postgres_session)) -> ConversationService:
    """Conversation service dependency"""
    return ConversationService(session)

# Helper functions to avoid code duplication
async def _create_conversation_impl(
    user_id: str,
    conversation_data: ConversationCreateDto,
    conversation_service: ConversationService
):
    """Implementation for create conversation"""
    logger.info(f"🚀 API: Create conversation requested for user: {user_id}")
    
    try:
        conversation = await conversation_service.create_conversation(user_id, conversation_data)
        logger.info(f"✅ API: Conversation created successfully: {conversation.conversation_id}")
        return conversation
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Conversation creation validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ API: Conversation creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create conversation")

async def _get_user_conversations_impl(
    user_id: str,
    status: Optional[ConversationStatus] = None,
    limit: int = 20,
    offset: int = 0,
    conversation_service: ConversationService = None
):
    """Implementation for get user conversations"""
    logger.info(f"🚀 API: Get conversations requested for user: {user_id}")
    
    try:
        conversations = await conversation_service.get_user_conversations(user_id, status, limit, offset)
        logger.info(f"✅ API: Conversations retrieved for user: {user_id}, count: {len(conversations.conversations)}")
        return conversations
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversations")

@router.post(
    "/",
    response_model=ConversationResponseDto,
    status_code=status.HTTP_201_CREATED,
    summary="Create conversation",
    description="Create a new conversation for the user"
)
async def create_conversation(
    user_id: str,
    conversation_data: ConversationCreateDto,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Create a new conversation (without trailing slash)"""
    return await _create_conversation_impl(user_id, conversation_data, conversation_service)

@router.post(
    "",
    response_model=ConversationResponseDto,
    status_code=status.HTTP_201_CREATED,
    summary="Create conversation",
    description="Create a new conversation for the user",
    include_in_schema=False
)
async def create_conversation_no_slash(
    user_id: str,
    conversation_data: ConversationCreateDto,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Create a new conversation (with trailing slash)"""
    return await _create_conversation_impl(user_id, conversation_data, conversation_service)

@router.get(
    "/",
    response_model=ConversationListResponseDto,
    summary="Get user conversations",
    description="Get conversations for a user with pagination and filtering"
)
async def get_user_conversations(
    user_id: str,
    status: Optional[ConversationStatus] = Query(None, description="Filter by conversation status"),
    limit: int = Query(20, ge=1, le=200, description="Number of conversations to return"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip"),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Get user conversations (without trailing slash)"""
    return await _get_user_conversations_impl(user_id, status, limit, offset, conversation_service)

@router.get(
    "",
    response_model=ConversationListResponseDto,
    summary="Get user conversations",
    description="Get conversations for a user with pagination and filtering",
    include_in_schema=False
)
async def get_user_conversations_no_slash(
    user_id: str,
    status: Optional[ConversationStatus] = Query(None, description="Filter by conversation status"),
    limit: int = Query(20, ge=1, le=200, description="Number of conversations to return"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip"),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Get user conversations (with trailing slash)"""
    return await _get_user_conversations_impl(user_id, status, limit, offset, conversation_service)

# Helper functions for individual conversation operations
async def _get_conversation_impl(
    user_id: str,
    conversation_id: str,
    include_messages: bool = False,
    conversation_service: ConversationService = None
):
    """Implementation for get conversation"""
    logger.info(f"🚀 API: Get conversation requested: {conversation_id}")
    
    try:
        conversation = await conversation_service.get_conversation_by_id(conversation_id, include_messages)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Verify ownership
        if hasattr(conversation, 'user_id') and conversation.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"✅ API: Conversation retrieved: {conversation_id}")
        return conversation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to get conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation")

async def _update_conversation_impl(
    user_id: str,
    conversation_id: str,
    update_data: ConversationUpdateDto,
    conversation_service: ConversationService
):
    """Implementation for update conversation"""
    logger.info(f"🚀 API: Update conversation requested: {conversation_id}")
    
    try:
        # First verify conversation exists and belongs to user
        existing_conversation = await conversation_service.get_conversation_by_id(conversation_id)
        if not existing_conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if existing_conversation.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        conversation = await conversation_service.update_conversation(conversation_id, update_data)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        logger.info(f"✅ API: Conversation updated successfully: {conversation_id}")
        return conversation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to update conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to update conversation")

async def _archive_conversation_impl(
    user_id: str,
    conversation_id: str,
    conversation_service: ConversationService
):
    """Implementation for archive conversation"""
    logger.info(f"🚀 API: Archive conversation requested: {conversation_id}")
    
    try:
        # Verify ownership
        conversation = await conversation_service.get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await conversation_service.archive_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        logger.info(f"✅ API: Conversation archived successfully: {conversation_id}")
        return {"message": "Conversation archived successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to archive conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to archive conversation")

async def _restore_conversation_impl(
    user_id: str,
    conversation_id: str,
    conversation_service: ConversationService
):
    """Implementation for restore conversation"""
    logger.info(f"🚀 API: Restore conversation requested: {conversation_id}")
    
    try:
        # Verify ownership
        conversation = await conversation_service.get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await conversation_service.restore_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        logger.info(f"✅ API: Conversation restored successfully: {conversation_id}")
        return {"message": "Conversation restored successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to restore conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to restore conversation")

@router.get(
    "/{conversation_id}",
    response_model=ConversationResponseDto,
    summary="Get conversation",
    description="Get conversation by ID"
)
async def get_conversation(
    user_id: str,
    conversation_id: str,
    include_messages: bool = Query(False, description="Include recent messages"),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Get conversation by ID (without trailing slash)"""
    return await _get_conversation_impl(user_id, conversation_id, include_messages, conversation_service)

@router.get(
    "/{conversation_id}/",
    response_model=ConversationResponseDto,
    summary="Get conversation",
    description="Get conversation by ID",
    include_in_schema=False
)
async def get_conversation_with_slash(
    user_id: str,
    conversation_id: str,
    include_messages: bool = Query(False, description="Include recent messages"),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Get conversation by ID (with trailing slash)"""
    return await _get_conversation_impl(user_id, conversation_id, include_messages, conversation_service)

@router.put(
    "/{conversation_id}",
    response_model=ConversationResponseDto,
    summary="Update conversation",
    description="Update conversation information"
)
async def update_conversation(
    user_id: str,
    conversation_id: str,
    update_data: ConversationUpdateDto,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Update conversation (without trailing slash)"""
    return await _update_conversation_impl(user_id, conversation_id, update_data, conversation_service)

@router.put(
    "/{conversation_id}/",
    response_model=ConversationResponseDto,
    summary="Update conversation",
    description="Update conversation information",
    include_in_schema=False
)
async def update_conversation_with_slash(
    user_id: str,
    conversation_id: str,
    update_data: ConversationUpdateDto,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Update conversation (with trailing slash)"""
    return await _update_conversation_impl(user_id, conversation_id, update_data, conversation_service)

@router.post(
    "/{conversation_id}/archive",
    summary="Archive conversation",
    description="Archive a conversation"
)
async def archive_conversation(
    user_id: str,
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Archive conversation (without trailing slash)"""
    return await _archive_conversation_impl(user_id, conversation_id, conversation_service)

@router.post(
    "/{conversation_id}/archive/",
    summary="Archive conversation",
    description="Archive a conversation",
    include_in_schema=False
)
async def archive_conversation_with_slash(
    user_id: str,
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Archive conversation (with trailing slash)"""
    return await _archive_conversation_impl(user_id, conversation_id, conversation_service)

@router.post(
    "/{conversation_id}/restore",
    summary="Restore conversation",
    description="Restore an archived conversation"
)
async def restore_conversation(
    user_id: str,
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Restore conversation (without trailing slash)"""
    return await _restore_conversation_impl(user_id, conversation_id, conversation_service)

@router.post(
    "/{conversation_id}/restore/",
    summary="Restore conversation",
    description="Restore an archived conversation",
    include_in_schema=False
)
async def restore_conversation_with_slash(
    user_id: str,
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Restore conversation (with trailing slash)"""
    return await _restore_conversation_impl(user_id, conversation_id, conversation_service)

@router.delete(
    "/{conversation_id}",
    summary="Delete conversation",
    description="Soft delete a conversation"
)
async def delete_conversation(
    user_id: str,
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Delete conversation"""
    logger.info(f"🚀 API: Delete conversation requested: {conversation_id}")
    
    try:
        # Verify ownership
        conversation = await conversation_service.get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await conversation_service.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        logger.info(f"✅ API: Conversation deleted successfully: {conversation_id}")
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to delete conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete conversation")

# Helper functions for search, recent, and stats endpoints
async def _search_conversations_impl(
    user_id: str,
    query: Optional[str] = None,
    status: Optional[ConversationStatus] = None,
    bot_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    conversation_service: ConversationService = None
):
    """Implementation for search conversations"""
    logger.info(f"🚀 API: Search conversations requested for user: {user_id}")
    
    try:
        # Parse dates if provided
        start_datetime = None
        end_datetime = None
        
        if start_date:
            from datetime import datetime
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        if end_date:
            from datetime import datetime
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        search_data = ConversationSearchDto(
            query=query,
            status=status,
            bot_id=bot_id,
            start_date=start_datetime,
            end_date=end_datetime,
            limit=limit,
            offset=offset
        )
        
        conversations = await conversation_service.search_conversations(user_id, search_data)
        logger.info(f"✅ API: Conversation search completed for user: {user_id}")
        return conversations
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Search validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ API: Failed to search conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to search conversations")

async def _get_recent_conversations_impl(
    user_id: str,
    days: int = 7,
    limit: int = 10,
    conversation_service: ConversationService = None
):
    """Implementation for get recent conversations"""
    logger.info(f"🚀 API: Get recent conversations requested for user: {user_id}")
    
    try:
        conversations = await conversation_service.get_recent_conversations(user_id, days, limit)
        logger.info(f"✅ API: Recent conversations retrieved for user: {user_id}")
        return conversations
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get recent conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recent conversations")

async def _get_conversation_stats_impl(
    user_id: str,
    conversation_service: ConversationService = None
):
    """Implementation for get conversation stats"""
    logger.info(f"🚀 API: Get conversation stats requested for user: {user_id}")
    
    try:
        stats = await conversation_service.get_conversation_stats(user_id)
        logger.info(f"✅ API: Conversation stats retrieved for user: {user_id}")
        return stats
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get conversation stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation statistics")

@router.get(
    "/search",
    response_model=ConversationListResponseDto,
    summary="Search conversations",
    description="Search user conversations with filters"
)
async def search_conversations(
    user_id: str,
    query: Optional[str] = Query(None, description="Search query"),
    status: Optional[ConversationStatus] = Query(None, description="Filter by status"),
    bot_id: Optional[str] = Query(None, description="Filter by bot ID"),
    start_date: Optional[str] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date filter (ISO format)"),
    limit: int = Query(20, ge=1, le=200, description="Number of conversations to return"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip"),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Search conversations (without trailing slash)"""
    return await _search_conversations_impl(
        user_id, query, status, bot_id, start_date, end_date,
        limit, offset, conversation_service
    )

@router.get(
    "/search/",
    response_model=ConversationListResponseDto,
    summary="Search conversations",
    description="Search user conversations with filters",
    include_in_schema=False
)
async def search_conversations_with_slash(
    user_id: str,
    query: Optional[str] = Query(None, description="Search query"),
    status: Optional[ConversationStatus] = Query(None, description="Filter by status"),
    bot_id: Optional[str] = Query(None, description="Filter by bot ID"),
    start_date: Optional[str] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date filter (ISO format)"),
    limit: int = Query(20, ge=1, le=200, description="Number of conversations to return"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip"),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Search conversations (with trailing slash)"""
    return await _search_conversations_impl(
        user_id, query, status, bot_id, start_date, end_date,
        limit, offset, conversation_service
    )

@router.get(
    "/recent",
    response_model=List[ConversationResponseDto],
    summary="Get recent conversations",
    description="Get recent conversations for a user"
)
async def get_recent_conversations(
    user_id: str,
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=50, description="Number of conversations to return"),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Get recent conversations (without trailing slash)"""
    return await _get_recent_conversations_impl(user_id, days, limit, conversation_service)

@router.get(
    "/recent/",
    response_model=List[ConversationResponseDto],
    summary="Get recent conversations",
    description="Get recent conversations for a user",
    include_in_schema=False
)
async def get_recent_conversations_with_slash(
    user_id: str,
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=50, description="Number of conversations to return"),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Get recent conversations (with trailing slash)"""
    return await _get_recent_conversations_impl(user_id, days, limit, conversation_service)

@router.get(
    "/stats",
    response_model=ConversationStatsDto,
    summary="Get conversation statistics",
    description="Get conversation statistics for a user"
)
async def get_conversation_stats(
    user_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Get conversation statistics (without trailing slash)"""
    return await _get_conversation_stats_impl(user_id, conversation_service)

@router.get(
    "/stats/",
    response_model=ConversationStatsDto,
    summary="Get conversation statistics",
    description="Get conversation statistics for a user",
    include_in_schema=False
)
async def get_conversation_stats_with_slash(
    user_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Get conversation statistics (with trailing slash)"""
    return await _get_conversation_stats_impl(user_id, conversation_service)

__all__ = ["router"]