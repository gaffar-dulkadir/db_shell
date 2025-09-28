"""
Conversation Service for Chat Marketplace Service
Handles conversation operations
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from datalayer.repository.conversation_repository import ConversationRepository
from datalayer.repository.bot_repository import BotRepository
from datalayer.model.sqlalchemy_models import Conversation
from datalayer.model.dto.chat_dto import (
    ConversationCreateDto, ConversationUpdateDto, ConversationResponseDto,
    ConversationWithMessagesDto, ConversationListResponseDto, ConversationStatus,
    ConversationSearchDto, ConversationStatsDto
)

logger = logging.getLogger(__name__)

class ConversationService:
    """Service for conversation operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.conversation_repo = ConversationRepository(session)
        self.bot_repo = BotRepository(session)
        logger.debug("✅ ConversationService initialized")
    
    async def create_conversation(self, user_id: str, conversation_data: ConversationCreateDto) -> ConversationResponseDto:
        """Create a new conversation"""
        logger.info(f"📝 Creating conversation for user: {user_id}")
        
        try:
            # Validate bot if specified
            if conversation_data.bot_id:
                bot = await self.bot_repo.get_by_id(conversation_data.bot_id)
                if not bot:
                    raise ValueError(f"Bot with ID {conversation_data.bot_id} not found")
            
            # Create conversation
            conversation = Conversation(
                user_id=user_id,
                bot_id=conversation_data.bot_id,
                title=conversation_data.title,
                description=conversation_data.description,
                custom_metadata=conversation_data.metadata,
                status=ConversationStatus.ACTIVE
            )
            
            saved_conversation = await self.conversation_repo.save(conversation)
            await self.session.commit()
            
            logger.info(f"✅ Conversation created successfully: {saved_conversation.conversation_id}")
            return self._conversation_to_dto(saved_conversation)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to create conversation: {e}")
            raise
    
    async def get_conversation_by_id(self, conversation_id: str, include_messages: bool = False) -> Optional[ConversationResponseDto]:
        """Get conversation by ID"""
        logger.debug(f"🔍 Getting conversation: {conversation_id}")
        
        try:
            if include_messages:
                conversation = await self.conversation_repo.get_with_messages(conversation_id)
                if conversation:
                    return self._conversation_with_messages_to_dto(conversation)
            else:
                conversation = await self.conversation_repo.get_by_id(conversation_id)
                if conversation:
                    return self._conversation_to_dto(conversation)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation: {e}")
            raise
    
    async def get_user_conversations(
        self, 
        user_id: str, 
        status: Optional[ConversationStatus] = None,
        limit: int = 20, 
        offset: int = 0
    ) -> ConversationListResponseDto:
        """Get conversations for a user"""
        logger.debug(f"🔍 Getting conversations for user: {user_id}")
        
        try:
            conversations = await self.conversation_repo.get_by_user_id(
                user_id, limit + 1, offset, status
            )
            
            # Check if there are more results
            has_next = len(conversations) > limit
            if has_next:
                conversations = conversations[:limit]
            
            has_prev = offset > 0
            
            # Get total count
            total = await self.conversation_repo.count_by_user(user_id, status)
            
            conversation_dtos = [self._conversation_to_dto(conv) for conv in conversations]
            
            return ConversationListResponseDto(
                conversations=conversation_dtos,
                total=total,
                page=(offset // limit) + 1,
                limit=limit,
                has_next=has_next,
                has_prev=has_prev
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get user conversations: {e}")
            raise
    
    async def update_conversation(
        self, 
        conversation_id: str, 
        update_data: ConversationUpdateDto
    ) -> Optional[ConversationResponseDto]:
        """Update conversation"""
        logger.info(f"📝 Updating conversation: {conversation_id}")
        
        try:
            conversation = await self.conversation_repo.get_by_id(conversation_id)
            if not conversation:
                return None
            
            # Update fields
            if update_data.title is not None:
                conversation.title = update_data.title
            if update_data.description is not None:
                conversation.description = update_data.description
            if update_data.status is not None:
                conversation.status = update_data.status
            if update_data.metadata is not None:
                conversation.custom_metadata = update_data.metadata
            
            conversation.updated_at = datetime.utcnow()
            
            updated_conversation = await self.conversation_repo.save(conversation)
            await self.session.commit()
            
            logger.info(f"✅ Conversation updated successfully: {conversation_id}")
            return self._conversation_to_dto(updated_conversation)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to update conversation: {e}")
            raise
    
    async def archive_conversation(self, conversation_id: str) -> bool:
        """Archive a conversation"""
        logger.info(f"📁 Archiving conversation: {conversation_id}")
        
        try:
            success = await self.conversation_repo.archive_conversation(conversation_id)
            
            if success:
                logger.info(f"✅ Conversation archived successfully: {conversation_id}")
            else:
                logger.warning(f"⚠️ Conversation not found for archiving: {conversation_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to archive conversation: {e}")
            raise
    
    async def restore_conversation(self, conversation_id: str) -> bool:
        """Restore an archived conversation"""
        logger.info(f"📤 Restoring conversation: {conversation_id}")
        
        try:
            success = await self.conversation_repo.restore_conversation(conversation_id)
            
            if success:
                logger.info(f"✅ Conversation restored successfully: {conversation_id}")
            else:
                logger.warning(f"⚠️ Conversation not found for restoring: {conversation_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to restore conversation: {e}")
            raise
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Soft delete a conversation"""
        logger.info(f"🗑️ Deleting conversation: {conversation_id}")
        
        try:
            success = await self.conversation_repo.delete_conversation(conversation_id)
            
            if success:
                logger.info(f"✅ Conversation deleted successfully: {conversation_id}")
            else:
                logger.warning(f"⚠️ Conversation not found for deletion: {conversation_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to delete conversation: {e}")
            raise
    
    async def search_conversations(
        self, 
        user_id: str, 
        search_data: ConversationSearchDto
    ) -> ConversationListResponseDto:
        """Search user conversations"""
        logger.debug(f"🔍 Searching conversations for user: {user_id}")
        
        try:
            conversations = await self.conversation_repo.search_conversations(
                user_id=user_id,
                query=search_data.query or "",
                status=search_data.status,
                bot_id=search_data.bot_id,
                limit=search_data.limit + 1,
                offset=search_data.offset
            )
            
            # Check if there are more results
            has_next = len(conversations) > search_data.limit
            if has_next:
                conversations = conversations[:search_data.limit]
            
            has_prev = search_data.offset > 0
            
            # For search, we'll estimate total based on current results
            total = len(conversations) + search_data.offset
            if has_next:
                total += 1  # At least one more page
            
            conversation_dtos = [self._conversation_to_dto(conv) for conv in conversations]
            
            return ConversationListResponseDto(
                conversations=conversation_dtos,
                total=total,
                page=(search_data.offset // search_data.limit) + 1,
                limit=search_data.limit,
                has_next=has_next,
                has_prev=has_prev
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to search conversations: {e}")
            raise
    
    async def get_recent_conversations(self, user_id: str, days: int = 7, limit: int = 10) -> List[ConversationResponseDto]:
        """Get recent conversations for a user"""
        logger.debug(f"🔍 Getting recent conversations for user: {user_id}")
        
        try:
            conversations = await self.conversation_repo.get_recent_conversations(user_id, days, limit)
            return [self._conversation_to_dto(conv) for conv in conversations]
            
        except Exception as e:
            logger.error(f"❌ Failed to get recent conversations: {e}")
            raise
    
    async def get_conversation_stats(self, user_id: str) -> ConversationStatsDto:
        """Get conversation statistics for a user"""
        logger.debug(f"📊 Getting conversation stats for user: {user_id}")
        
        try:
            stats = await self.conversation_repo.get_conversation_stats(user_id)
            
            return ConversationStatsDto(
                total_conversations=stats["total_conversations"],
                active_conversations=stats["active_conversations"],
                archived_conversations=stats["archived_conversations"],
                total_messages=0,  # Will be calculated by message service
                today_messages=0,  # Will be calculated by message service
                avg_messages_per_conversation=0.0  # Will be calculated by message service
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation stats: {e}")
            raise
    
    async def update_last_message_time(self, conversation_id: str, message_time: datetime) -> bool:
        """Update conversation's last message timestamp"""
        logger.debug(f"⏰ Updating last message time for conversation: {conversation_id}")
        
        try:
            success = await self.conversation_repo.update_last_message_time(conversation_id, message_time)
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to update last message time: {e}")
            raise
    
    async def get_conversations_with_message_count(
        self, 
        user_id: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get conversations with message count"""
        logger.debug(f"🔍 Getting conversations with message count for user: {user_id}")
        
        try:
            conversations_with_count = await self.conversation_repo.get_conversations_with_message_count(
                user_id, limit, offset
            )
            
            result = []
            for item in conversations_with_count:
                conv_dto = self._conversation_to_dto(item["conversation"])
                result.append({
                    "conversation": conv_dto,
                    "message_count": item["message_count"]
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversations with message count: {e}")
            raise
    
    def _conversation_to_dto(self, conversation: Conversation) -> ConversationResponseDto:
        """Convert Conversation model to ConversationResponseDto"""
        return ConversationResponseDto(
            conversation_id=conversation.conversation_id,
            user_id=conversation.user_id,
            bot_id=conversation.bot_id,
            title=conversation.title,
            description=conversation.description,
            status=conversation.status,
            metadata=conversation.custom_metadata,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            last_message_at=conversation.last_message_at,
            message_count=len(conversation.messages) if hasattr(conversation, 'messages') and conversation.messages else 0
        )
    
    def _conversation_with_messages_to_dto(self, conversation: Conversation) -> ConversationWithMessagesDto:
        """Convert Conversation model with messages to ConversationWithMessagesDto"""
        from .message_service import MessageService
        
        conv_dto = self._conversation_to_dto(conversation)
        
        message_dtos = []
        if hasattr(conversation, 'messages') and conversation.messages:
            message_dtos = [MessageService._message_to_dto(msg) for msg in conversation.messages]
        
        bot_dto = None
        if hasattr(conversation, 'bot') and conversation.bot:
            from .bot_service import BotService
            bot_dto = BotService._bot_to_dto(conversation.bot)
        
        return ConversationWithMessagesDto(
            **conv_dto.dict(),
            messages=message_dtos,
            bot=bot_dto
        )

__all__ = ["ConversationService"]