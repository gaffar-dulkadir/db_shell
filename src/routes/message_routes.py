"""
Message Routes for Chat Marketplace Service
Handles message, document, and memory management endpoints
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from datalayer.database import get_postgres_session
from sqlalchemy.ext.asyncio import AsyncSession
from services.message_service import MessageService
from datalayer.model.dto.chat_dto import (
    MessageCreateDto, MessageUpdateDto, MessageResponseDto, MessageWithDocumentsDto,
    MessageListResponseDto, MessageType, MessageSearchDto, MessageStatsDto,
    DocumentCreateDto, DocumentResponseDto, DocumentListResponseDto,
    MemoryHistoryCreateDto, MemoryHistoryUpdateDto, MemoryHistoryResponseDto,
    MemoryHistoryListResponseDto
)

logger = logging.getLogger(__name__)

# Router configuration
router = APIRouter(
    prefix="/users/{user_id}/conversations/{conversation_id}/messages",
    tags=["Messages"],
    responses={404: {"description": "Not found"}}
)

# Dependency functions
def get_message_service(session: AsyncSession = Depends(get_postgres_session)) -> MessageService:
    """Message service dependency"""
    return MessageService(session)

@router.post(
    "/",
    response_model=MessageResponseDto,
    status_code=status.HTTP_201_CREATED,
    summary="Create message",
    description="Create a new message in the conversation"
)
async def create_message(
    user_id: str,
    conversation_id: str,
    message_data: MessageCreateDto,
    message_service: MessageService = Depends(get_message_service)
):
    """Create a new message"""
    logger.info(f"🚀 API: Create message requested in conversation: {conversation_id}")
    
    try:
        message = await message_service.create_message(conversation_id, message_data)
        logger.info(f"✅ API: Message created successfully: {message.message_id}")
        return message
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Message creation validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ API: Message creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create message")

@router.get(
    "/",
    response_model=MessageListResponseDto,
    summary="Get conversation messages",
    description="Get messages for a conversation with pagination"
)
async def get_conversation_messages(
    user_id: str,
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    include_deleted: bool = Query(False, description="Include deleted messages"),
    message_service: MessageService = Depends(get_message_service)
):
    """Get conversation messages"""
    logger.info(f"🚀 API: Get messages requested for conversation: {conversation_id}")
    
    try:
        messages = await message_service.get_conversation_messages(
            conversation_id, limit, offset, include_deleted
        )
        logger.info(f"✅ API: Messages retrieved for conversation: {conversation_id}, count: {len(messages.messages)}")
        return messages
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

@router.get(
    "/{message_id}",
    response_model=MessageResponseDto,
    summary="Get message",
    description="Get message by ID"
)
async def get_message(
    user_id: str,
    conversation_id: str,
    message_id: str,
    include_documents: bool = Query(False, description="Include message documents"),
    message_service: MessageService = Depends(get_message_service)
):
    """Get message by ID"""
    logger.info(f"🚀 API: Get message requested: {message_id}")
    
    try:
        message = await message_service.get_message_by_id(message_id, include_documents)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Verify the message belongs to the specified conversation
        if message.conversation_id != conversation_id:
            raise HTTPException(status_code=404, detail="Message not found in this conversation")
        
        logger.info(f"✅ API: Message retrieved: {message_id}")
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to get message: {e}")
        raise HTTPException(status_code=500, detail="Failed to get message")

@router.put(
    "/{message_id}",
    response_model=MessageResponseDto,
    summary="Update message",
    description="Update message content and metadata"
)
async def update_message(
    user_id: str,
    conversation_id: str,
    message_id: str,
    update_data: MessageUpdateDto,
    message_service: MessageService = Depends(get_message_service)
):
    """Update message"""
    logger.info(f"🚀 API: Update message requested: {message_id}")
    
    try:
        # Verify message exists and belongs to conversation
        existing_message = await message_service.get_message_by_id(message_id)
        if not existing_message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        if existing_message.conversation_id != conversation_id:
            raise HTTPException(status_code=404, detail="Message not found in this conversation")
        
        # Verify user can edit this message (only sender can edit)
        if existing_message.sender_type == "user" and existing_message.sender_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        message = await message_service.update_message(message_id, update_data)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        logger.info(f"✅ API: Message updated successfully: {message_id}")
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to update message: {e}")
        raise HTTPException(status_code=500, detail="Failed to update message")

@router.delete(
    "/{message_id}",
    summary="Delete message",
    description="Soft delete a message"
)
async def delete_message(
    user_id: str,
    conversation_id: str,
    message_id: str,
    message_service: MessageService = Depends(get_message_service)
):
    """Delete message"""
    logger.info(f"🚀 API: Delete message requested: {message_id}")
    
    try:
        # Verify message exists and belongs to conversation
        existing_message = await message_service.get_message_by_id(message_id)
        if not existing_message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        if existing_message.conversation_id != conversation_id:
            raise HTTPException(status_code=404, detail="Message not found in this conversation")
        
        # Verify user can delete this message
        if existing_message.sender_type == "user" and existing_message.sender_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await message_service.delete_message(message_id)
        if not success:
            raise HTTPException(status_code=404, detail="Message not found")
        
        logger.info(f"✅ API: Message deleted successfully: {message_id}")
        return {"message": "Message deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to delete message: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete message")

@router.get(
    "/search",
    response_model=MessageListResponseDto,
    summary="Search messages",
    description="Search messages in the conversation"
)
async def search_messages(
    user_id: str,
    conversation_id: str,
    query: Optional[str] = Query(None, description="Search query"),
    message_type: Optional[MessageType] = Query(None, description="Filter by message type"),
    sender_type: Optional[str] = Query(None, description="Filter by sender type (user/bot)"),
    start_date: Optional[str] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date filter (ISO format)"),
    limit: int = Query(20, ge=1, le=200, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    message_service: MessageService = Depends(get_message_service)
):
    """Search messages"""
    logger.info(f"🚀 API: Search messages requested for conversation: {conversation_id}")
    
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
        
        search_data = MessageSearchDto(
            query=query,
            message_type=message_type,
            sender_type=sender_type,
            start_date=start_datetime,
            end_date=end_datetime,
            limit=limit,
            offset=offset
        )
        
        messages = await message_service.search_messages(conversation_id, search_data)
        logger.info(f"✅ API: Message search completed for conversation: {conversation_id}")
        return messages
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Search validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ API: Failed to search messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to search messages")

@router.get(
    "/recent",
    response_model=List[MessageResponseDto],
    summary="Get recent messages",
    description="Get recent messages in the conversation"
)
async def get_recent_messages(
    user_id: str,
    conversation_id: str,
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    limit: int = Query(50, ge=1, le=200, description="Number of messages to return"),
    message_service: MessageService = Depends(get_message_service)
):
    """Get recent messages"""
    logger.info(f"🚀 API: Get recent messages requested for conversation: {conversation_id}")
    
    try:
        messages = await message_service.get_recent_messages(conversation_id, hours, limit)
        logger.info(f"✅ API: Recent messages retrieved for conversation: {conversation_id}")
        return messages
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get recent messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recent messages")

@router.get(
    "/stats",
    response_model=MessageStatsDto,
    summary="Get message statistics",
    description="Get message statistics for the conversation"
)
async def get_message_stats(
    user_id: str,
    conversation_id: str,
    message_service: MessageService = Depends(get_message_service)
):
    """Get message statistics"""
    logger.info(f"🚀 API: Get message stats requested for conversation: {conversation_id}")
    
    try:
        stats = await message_service.get_message_stats(conversation_id)
        logger.info(f"✅ API: Message stats retrieved for conversation: {conversation_id}")
        return stats
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get message stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get message statistics")

# Document endpoints
@router.post(
    "/{message_id}/documents",
    response_model=DocumentResponseDto,
    status_code=status.HTTP_201_CREATED,
    summary="Add document to message",
    description="Add a document attachment to a message"
)
async def add_document_to_message(
    user_id: str,
    conversation_id: str,
    message_id: str,
    document_data: DocumentCreateDto,
    message_service: MessageService = Depends(get_message_service)
):
    """Add document to message"""
    logger.info(f"🚀 API: Add document requested for message: {message_id}")
    
    try:
        # Verify message exists and belongs to conversation
        message = await message_service.get_message_by_id(message_id)
        if not message or message.conversation_id != conversation_id:
            raise HTTPException(status_code=404, detail="Message not found")
        
        document = await message_service.add_document_to_message(message_id, document_data)
        logger.info(f"✅ API: Document added successfully: {document.document_id}")
        return document
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Document creation validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to add document: {e}")
        raise HTTPException(status_code=500, detail="Failed to add document")

@router.get(
    "/{message_id}/documents",
    response_model=List[DocumentResponseDto],
    summary="Get message documents",
    description="Get all documents attached to a message"
)
async def get_message_documents(
    user_id: str,
    conversation_id: str,
    message_id: str,
    message_service: MessageService = Depends(get_message_service)
):
    """Get message documents"""
    logger.info(f"🚀 API: Get documents requested for message: {message_id}")
    
    try:
        # Verify message exists and belongs to conversation
        message = await message_service.get_message_by_id(message_id)
        if not message or message.conversation_id != conversation_id:
            raise HTTPException(status_code=404, detail="Message not found")
        
        documents = await message_service.get_message_documents(message_id)
        logger.info(f"✅ API: Documents retrieved for message: {message_id}")
        return documents
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Failed to get message documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to get message documents")

# Document routes for conversation-level access
documents_router = APIRouter(
    prefix="/users/{user_id}/conversations/{conversation_id}/documents",
    tags=["Documents"],
    responses={404: {"description": "Not found"}}
)

@documents_router.get(
    "/",
    response_model=DocumentListResponseDto,
    summary="Get conversation documents",
    description="Get all documents in the conversation with pagination"
)
async def get_conversation_documents(
    user_id: str,
    conversation_id: str,
    limit: int = Query(100, ge=1, le=200, description="Number of documents to return"),
    offset: int = Query(0, ge=0, description="Number of documents to skip"),
    message_service: MessageService = Depends(get_message_service)
):
    """Get conversation documents"""
    logger.info(f"🚀 API: Get documents requested for conversation: {conversation_id}")
    
    try:
        documents = await message_service.get_conversation_documents(conversation_id, limit, offset)
        logger.info(f"✅ API: Documents retrieved for conversation: {conversation_id}")
        return documents
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get conversation documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation documents")

# Memory endpoints
memory_router = APIRouter(
    prefix="/users/{user_id}/conversations/{conversation_id}/memory-history",
    tags=["Memory History"],
    responses={404: {"description": "Not found"}}
)

@memory_router.post(
    "/",
    response_model=MemoryHistoryResponseDto,
    status_code=status.HTTP_201_CREATED,
    summary="Add memory",
    description="Add a memory entry to the conversation"
)
async def add_memory(
    user_id: str,
    conversation_id: str,
    memory_data: MemoryHistoryCreateDto,
    message_service: MessageService = Depends(get_message_service)
):
    """Add memory to conversation"""
    logger.info(f"🚀 API: Add memory requested for conversation: {conversation_id}")
    
    try:
        memory = await message_service.add_memory(conversation_id, memory_data)
        logger.info(f"✅ API: Memory added successfully: {memory.memory_id}")
        return memory
        
    except ValueError as e:
        logger.warning(f"⚠️ API: Memory creation validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ API: Failed to add memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to add memory")

@memory_router.get(
    "/",
    response_model=MemoryHistoryListResponseDto,
    summary="Get conversation memories",
    description="Get memory entries for the conversation"
)
async def get_conversation_memories(
    user_id: str,
    conversation_id: str,
    memory_type: Optional[str] = Query(None, description="Filter by memory type"),
    limit: int = Query(100, ge=1, le=200, description="Number of memories to return"),
    offset: int = Query(0, ge=0, description="Number of memories to skip"),
    message_service: MessageService = Depends(get_message_service)
):
    """Get conversation memories"""
    logger.info(f"🚀 API: Get memories requested for conversation: {conversation_id}")
    
    try:
        memories = await message_service.get_conversation_memories(
            conversation_id, memory_type, limit, offset
        )
        logger.info(f"✅ API: Memories retrieved for conversation: {conversation_id}")
        return memories
        
    except Exception as e:
        logger.error(f"❌ API: Failed to get conversation memories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation memories")

__all__ = ["router", "documents_router", "memory_router"]