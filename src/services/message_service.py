"""
Message Service for Chat Marketplace Service
Handles message, document, and memory history operations
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from datalayer.repository.message_repository import MessageRepository, DocumentRepository, MemoryHistoryRepository
from datalayer.repository.conversation_repository import ConversationRepository
from datalayer.model.sqlalchemy_models import Message, Document, MemoryHistory
from datalayer.model.dto.chat_dto import (
    MessageCreateDto, MessageUpdateDto, MessageResponseDto, MessageWithDocumentsDto,
    MessageListResponseDto, MessageType, MessageSearchDto, MessageStatsDto,
    DocumentCreateDto, DocumentResponseDto, DocumentListResponseDto,
    MemoryHistoryCreateDto, MemoryHistoryUpdateDto, MemoryHistoryResponseDto,
    MemoryHistoryListResponseDto
)

logger = logging.getLogger(__name__)

class MessageService:
    """Service for message operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.message_repo = MessageRepository(session)
        self.document_repo = DocumentRepository(session)
        self.memory_repo = MemoryHistoryRepository(session)
        self.conversation_repo = ConversationRepository(session)
        logger.debug("✅ MessageService initialized")
    
    async def create_message(self, conversation_id: str, message_data: MessageCreateDto) -> MessageResponseDto:
        """Create a new message"""
        logger.info(f"📝 Creating message in conversation: {conversation_id}")
        
        try:
            # Verify conversation exists
            conversation = await self.conversation_repo.get_by_id(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            # Get parent message ID (last message in conversation for threading)
            last_message = await self.message_repo.get_last_message(conversation_id)
            parent_message_id = last_message.message_id if last_message else None
            
            # Create message
            message = Message(
                conversation_id=conversation_id,
                parent_message_id=parent_message_id,  # This will be set by trigger too
                sender_type=message_data.sender_type,
                sender_id=message_data.sender_id,
                message_type=message_data.message_type,
                content=message_data.content,
                custom_metadata=message_data.metadata
            )
            
            saved_message = await self.message_repo.save(message)
            
            # Update conversation's last message time
            await self.conversation_repo.update_last_message_time(
                conversation_id, saved_message.created_at
            )
            
            await self.session.commit()
            
            logger.info(f"✅ Message created successfully: {saved_message.message_id}")
            return self._message_to_dto(saved_message)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to create message: {e}")
            raise
    
    async def get_message_by_id(self, message_id: str, include_documents: bool = False) -> Optional[MessageResponseDto]:
        """Get message by ID"""
        logger.debug(f"🔍 Getting message: {message_id}")
        
        try:
            if include_documents:
                message = await self.message_repo.get_with_documents(message_id)
                if message:
                    return self._message_with_documents_to_dto(message)
            else:
                message = await self.message_repo.get_by_id(message_id)
                if message:
                    return self._message_to_dto(message)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get message: {e}")
            raise
    
    async def get_conversation_messages(
        self, 
        conversation_id: str, 
        limit: int = 50, 
        offset: int = 0,
        include_deleted: bool = False
    ) -> MessageListResponseDto:
        """Get messages for a conversation"""
        logger.debug(f"🔍 Getting messages for conversation: {conversation_id}")
        
        try:
            messages = await self.message_repo.get_by_conversation(
                conversation_id, limit + 1, offset, include_deleted
            )
            
            # Check if there are more results
            has_next = len(messages) > limit
            if has_next:
                messages = messages[:limit]
            
            has_prev = offset > 0
            
            # Get total count
            total = await self.message_repo.count_by_conversation(conversation_id, include_deleted)
            
            message_dtos = [self._message_to_dto(msg) for msg in messages]
            
            return MessageListResponseDto(
                messages=message_dtos,
                total=total,
                page=(offset // limit) + 1,
                limit=limit,
                has_next=has_next,
                has_prev=has_prev
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation messages: {e}")
            raise
    
    async def update_message(self, message_id: str, update_data: MessageUpdateDto) -> Optional[MessageResponseDto]:
        """Update message"""
        logger.info(f"📝 Updating message: {message_id}")
        
        try:
            message = await self.message_repo.get_by_id(message_id)
            if not message:
                return None
            
            # Update fields
            if update_data.content is not None:
                message.content = update_data.content
                # Mark as edited if content changed
                if not message.is_edited:
                    await self.message_repo.mark_as_edited(message_id)
            
            if update_data.metadata is not None:
                message.custom_metadata = update_data.metadata
            
            message.updated_at = datetime.utcnow()
            
            updated_message = await self.message_repo.save(message)
            await self.session.commit()
            
            logger.info(f"✅ Message updated successfully: {message_id}")
            return self._message_to_dto(updated_message)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to update message: {e}")
            raise
    
    async def delete_message(self, message_id: str) -> bool:
        """Soft delete a message"""
        logger.info(f"🗑️ Deleting message: {message_id}")
        
        try:
            success = await self.message_repo.soft_delete_message(message_id)
            
            if success:
                logger.info(f"✅ Message deleted successfully: {message_id}")
            else:
                logger.warning(f"⚠️ Message not found for deletion: {message_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to delete message: {e}")
            raise
    
    async def search_messages(
        self, 
        conversation_id: str, 
        search_data: MessageSearchDto
    ) -> MessageListResponseDto:
        """Search messages in a conversation"""
        logger.debug(f"🔍 Searching messages in conversation: {conversation_id}")
        
        try:
            messages = await self.message_repo.search_messages(
                conversation_id=conversation_id,
                query=search_data.query or "",
                message_type=search_data.message_type,
                sender_type=search_data.sender_type,
                limit=search_data.limit + 1,
                offset=search_data.offset
            )
            
            # Check if there are more results
            has_next = len(messages) > search_data.limit
            if has_next:
                messages = messages[:search_data.limit]
            
            has_prev = search_data.offset > 0
            
            # Estimate total for search results
            total = len(messages) + search_data.offset
            if has_next:
                total += 1
            
            message_dtos = [self._message_to_dto(msg) for msg in messages]
            
            return MessageListResponseDto(
                messages=message_dtos,
                total=total,
                page=(search_data.offset // search_data.limit) + 1,
                limit=search_data.limit,
                has_next=has_next,
                has_prev=has_prev
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to search messages: {e}")
            raise
    
    async def get_recent_messages(self, conversation_id: str, hours: int = 24, limit: int = 50) -> List[MessageResponseDto]:
        """Get recent messages"""
        logger.debug(f"🔍 Getting recent messages for conversation: {conversation_id}")
        
        try:
            messages = await self.message_repo.get_recent_messages(conversation_id, hours, limit)
            return [self._message_to_dto(msg) for msg in messages]
            
        except Exception as e:
            logger.error(f"❌ Failed to get recent messages: {e}")
            raise
    
    async def get_message_stats(self, conversation_id: str) -> MessageStatsDto:
        """Get message statistics for a conversation"""
        logger.debug(f"📊 Getting message stats for conversation: {conversation_id}")
        
        try:
            total_messages = await self.message_repo.count_by_conversation(conversation_id)
            user_messages = await self.message_repo.count_by_sender(conversation_id, "user")
            bot_messages = await self.message_repo.count_by_sender(conversation_id, "bot")
            
            # Get recent messages for today count
            recent_messages = await self.message_repo.get_recent_messages(conversation_id, 24, 1000)
            today_messages = len(recent_messages)
            
            # Calculate average message length
            all_messages = await self.message_repo.get_by_conversation(conversation_id, 1000, 0)
            avg_message_length = 0.0
            if all_messages:
                total_length = sum(len(msg.content) for msg in all_messages)
                avg_message_length = total_length / len(all_messages)
            
            # Count message types
            message_types = {}
            for msg in all_messages:
                msg_type = msg.message_type.value if hasattr(msg.message_type, 'value') else str(msg.message_type)
                message_types[msg_type] = message_types.get(msg_type, 0) + 1
            
            return MessageStatsDto(
                total_messages=total_messages,
                user_messages=user_messages,
                bot_messages=bot_messages,
                today_messages=today_messages,
                message_types=message_types,
                avg_message_length=avg_message_length
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get message stats: {e}")
            raise
    
    # Document operations
    async def add_document_to_message(self, message_id: str, document_data: DocumentCreateDto) -> DocumentResponseDto:
        """Add document to a message"""
        logger.info(f"📎 Adding document to message: {message_id}")
        
        try:
            # Verify message exists
            message = await self.message_repo.get_by_id(message_id)
            if not message:
                raise ValueError(f"Message {message_id} not found")
            
            # Create document
            document = Document(
                message_id=message_id,
                file_name=document_data.file_name,
                file_type=document_data.file_type,
                file_size=document_data.file_size,
                file_url=document_data.file_url,
                mime_type=document_data.mime_type,
                custom_metadata=document_data.metadata
            )
            
            saved_document = await self.document_repo.save(document)
            await self.session.commit()
            
            logger.info(f"✅ Document added successfully: {saved_document.document_id}")
            return self._document_to_dto(saved_document)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to add document: {e}")
            raise
    
    async def get_message_documents(self, message_id: str) -> List[DocumentResponseDto]:
        """Get documents for a message"""
        logger.debug(f"🔍 Getting documents for message: {message_id}")
        
        try:
            documents = await self.document_repo.get_by_message(message_id)
            return [self._document_to_dto(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"❌ Failed to get message documents: {e}")
            raise
    
    async def get_conversation_documents(
        self, 
        conversation_id: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> DocumentListResponseDto:
        """Get documents for a conversation"""
        logger.debug(f"🔍 Getting documents for conversation: {conversation_id}")
        
        try:
            documents = await self.document_repo.get_by_conversation(
                conversation_id, limit + 1, offset
            )
            
            # Check if there are more results
            has_next = len(documents) > limit
            if has_next:
                documents = documents[:limit]
            
            has_prev = offset > 0
            
            # Get total count
            total = await self.document_repo.count_by_conversation(conversation_id)
            
            document_dtos = [self._document_to_dto(doc) for doc in documents]
            
            return DocumentListResponseDto(
                documents=document_dtos,
                total=total,
                page=(offset // limit) + 1,
                limit=limit,
                has_next=has_next,
                has_prev=has_prev
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation documents: {e}")
            raise
    
    # Memory operations
    async def add_memory(self, conversation_id: str, memory_data: MemoryHistoryCreateDto) -> MemoryHistoryResponseDto:
        """Add memory to conversation"""
        logger.info(f"🧠 Adding memory to conversation: {conversation_id}")
        
        try:
            # Verify conversation exists
            conversation = await self.conversation_repo.get_by_id(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            # Use upsert to handle existing memories
            memory = await self.memory_repo.upsert_memory(
                conversation_id=conversation_id,
                memory_key=memory_data.memory_key,
                memory_value=memory_data.memory_value,
                memory_type=memory_data.memory_type,
                priority=memory_data.priority,
                expires_at=memory_data.expires_at
            )
            
            await self.session.commit()
            
            logger.info(f"✅ Memory added successfully: {memory.memory_id}")
            return self._memory_to_dto(memory)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to add memory: {e}")
            raise
    
    async def get_conversation_memories(
        self, 
        conversation_id: str, 
        memory_type: Optional[str] = None,
        limit: int = 100, 
        offset: int = 0
    ) -> MemoryHistoryListResponseDto:
        """Get memories for a conversation"""
        logger.debug(f"🔍 Getting memories for conversation: {conversation_id}")
        
        try:
            memories = await self.memory_repo.get_by_conversation(
                conversation_id, memory_type, limit + 1, offset
            )
            
            # Check if there are more results
            has_next = len(memories) > limit
            if has_next:
                memories = memories[:limit]
            
            has_prev = offset > 0
            
            # Get total count
            total = await self.memory_repo.count_by_conversation(conversation_id, memory_type)
            
            memory_dtos = [self._memory_to_dto(memory) for memory in memories]
            
            return MemoryHistoryListResponseDto(
                memories=memory_dtos,
                total=total,
                page=(offset // limit) + 1,
                limit=limit,
                has_next=has_next,
                has_prev=has_prev
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation memories: {e}")
            raise
    
    async def cleanup_expired_memories(self) -> int:
        """Clean up expired memories"""
        logger.info("🧹 Cleaning up expired memories")
        
        try:
            deleted_count = await self.memory_repo.cleanup_expired_memories()
            logger.info(f"✅ Cleaned up {deleted_count} expired memories")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup expired memories: {e}")
            raise
    
    @staticmethod
    def _message_to_dto(message: Message) -> MessageResponseDto:
        """Convert Message model to MessageResponseDto"""
        return MessageResponseDto(
            message_id=message.message_id,
            conversation_id=message.conversation_id,
            parent_message_id=message.parent_message_id,
            sender_type=message.sender_type,
            sender_id=message.sender_id,
            message_type=message.message_type,
            content=message.content,
            metadata=message.custom_metadata,
            is_edited=message.is_edited,
            is_deleted=message.is_deleted,
            created_at=message.created_at,
            updated_at=message.updated_at
        )
    
    def _message_with_documents_to_dto(self, message: Message) -> MessageWithDocumentsDto:
        """Convert Message model with documents to MessageWithDocumentsDto"""
        msg_dto = self._message_to_dto(message)
        
        document_dtos = []
        if hasattr(message, 'documents') and message.documents:
            document_dtos = [self._document_to_dto(doc) for doc in message.documents]
        
        parent_msg_dto = None
        if hasattr(message, 'parent_message') and message.parent_message:
            parent_msg_dto = self._message_to_dto(message.parent_message)
        
        return MessageWithDocumentsDto(
            **msg_dto.dict(),
            documents=document_dtos,
            parent_message=parent_msg_dto
        )
    
    @staticmethod
    def _document_to_dto(document: Document) -> DocumentResponseDto:
        """Convert Document model to DocumentResponseDto"""
        return DocumentResponseDto(
            document_id=document.document_id,
            message_id=document.message_id,
            file_name=document.file_name,
            file_type=document.file_type,
            file_size=document.file_size,
            file_url=document.file_url,
            mime_type=document.mime_type,
            metadata=document.custom_metadata,
            created_at=document.created_at
        )
    
    @staticmethod
    def _memory_to_dto(memory: MemoryHistory) -> MemoryHistoryResponseDto:
        """Convert MemoryHistory model to MemoryHistoryResponseDto"""
        return MemoryHistoryResponseDto(
            memory_id=memory.memory_id,
            conversation_id=memory.conversation_id,
            memory_key=memory.memory_key,
            memory_value=memory.memory_value,
            memory_type=memory.memory_type,
            priority=memory.priority,
            expires_at=memory.expires_at,
            created_at=memory.created_at,
            updated_at=memory.updated_at
        )

__all__ = ["MessageService"]