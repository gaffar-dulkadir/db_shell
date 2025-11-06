"""
Message Repository for Chat Marketplace Service
Handles Message, Document, and MemoryHistory operations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, update, delete, and_, or_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from ._base_repository import AsyncBaseRepository
from ..model.sqlalchemy_models import Message, Document, MemoryHistory, Conversation
from ..model.dto.chat_dto import MessageType

class MessageRepository(AsyncBaseRepository[Message]):
    """Repository for Message operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)
    
    async def get_by_conversation(
        self, 
        conversation_id: str, 
        limit: int = 50, 
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[Message]:
        """Get messages by conversation ID"""
        stmt = select(Message).where(Message.message_conversation_id == conversation_id)
        
        if not include_deleted:
            stmt = stmt.where(Message.is_deleted == False)
        
        stmt = (
            stmt.order_by(asc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_with_documents(self, message_id: str) -> Optional[Message]:
        """Get message with documents"""
        stmt = (
            select(Message)
            .options(selectinload(Message.documents))
            .where(Message.message_id == message_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_with_parent(self, message_id: str) -> Optional[Message]:
        """Get message with parent message"""
        stmt = (
            select(Message)
            .options(selectinload(Message.parent_message))
            .where(Message.message_id == message_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_conversation_thread(
        self, 
        conversation_id: str, 
        start_message_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Message]:
        """Get message thread for a conversation"""
        stmt = (
            select(Message)
            .where(Message.message_conversation_id == conversation_id)
            .where(Message.is_deleted == False)
        )
        
        if start_message_id:
            # Get messages after the specified message
            start_message_stmt = select(Message.created_at).where(Message.message_id == start_message_id)
            start_time_result = await self.session.execute(start_message_stmt)
            start_time = start_time_result.scalar()
            
            if start_time:
                stmt = stmt.where(Message.created_at >= start_time)
        
        stmt = stmt.order_by(asc(Message.created_at)).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_recent_messages(
        self, 
        conversation_id: str, 
        hours: int = 24, 
        limit: int = 50
    ) -> List[Message]:
        """Get recent messages within specified hours"""
        since_time = datetime.utcnow() - timedelta(hours=hours)
        
        stmt = (
            select(Message)
            .where(Message.message_conversation_id == conversation_id)
            .where(Message.created_at >= since_time)
            .where(Message.is_deleted == False)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def search_messages(
        self,
        conversation_id: str,
        query: str,
        message_type: Optional[MessageType] = None,
        sender_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Message]:
        """Search messages by content"""
        stmt = (
            select(Message)
            .where(Message.message_conversation_id == conversation_id)
            .where(Message.content.ilike(f"%{query}%"))
            .where(Message.is_deleted == False)
        )
        
        if message_type:
            stmt = stmt.where(Message.message_type_db == message_type.value if hasattr(message_type, 'value') else str(message_type))
        
        if sender_type:
            stmt = stmt.where(Message.message_role == sender_type)
        
        stmt = (
            stmt.order_by(desc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_last_message(self, conversation_id: str) -> Optional[Message]:
        """Get the last message in a conversation"""
        stmt = (
            select(Message)
            .where(Message.message_conversation_id == conversation_id)
            .where(Message.is_deleted == False)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def count_by_conversation(self, conversation_id: str, include_deleted: bool = False) -> int:
        """Count messages in a conversation"""
        stmt = select(func.count(Message.message_id)).where(Message.message_conversation_id == conversation_id)
        
        if not include_deleted:
            stmt = stmt.where(Message.is_deleted == False)
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def count_by_sender(self, conversation_id: str, sender_type: str) -> int:
        """Count messages by sender type in a conversation"""
        stmt = (
            select(func.count(Message.message_id))
            .where(Message.message_conversation_id == conversation_id)
            .where(Message.message_role == sender_type)
            .where(Message.is_deleted == False)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def soft_delete_message(self, message_id: str) -> bool:
        """Soft delete a message"""
        stmt = (
            update(Message)
            .where(Message.message_id == message_id)
            .values(
                is_deleted=True,
                updated_at=datetime.utcnow()
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
    
    async def mark_as_edited(self, message_id: str) -> bool:
        """Mark message as edited"""
        stmt = (
            update(Message)
            .where(Message.message_id == message_id)
            .values(
                is_edited=True,
                updated_at=datetime.utcnow()
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
    
    async def update_parent_message_id(self, message_id: str, parent_id: Optional[str]) -> bool:
        """Update message parent relationship"""
        stmt = (
            update(Message)
            .where(Message.message_id == message_id)
            .values(parent_message_id=parent_id)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

class DocumentRepository(AsyncBaseRepository[Document]):
    """Repository for Document operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Document)
    
    async def get_by_message(self, message_id: str) -> List[Document]:
        """Get documents by message ID"""
        stmt = (
            select(Document)
            .where(Document.document_message_id == message_id)
            .order_by(asc(Document.created_at))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_conversation(self, conversation_id: str, limit: int = 100, offset: int = 0) -> List[Document]:
        """Get documents by conversation ID"""
        stmt = (
            select(Document)
            .join(Message, Document.document_message_id == Message.message_id)
            .where(Message.message_conversation_id == conversation_id)
            .order_by(desc(Document.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_file_type(
        self, 
        conversation_id: str, 
        file_type: str, 
        limit: int = 50
    ) -> List[Document]:
        """Get documents by file type in a conversation"""
        stmt = (
            select(Document)
            .join(Message, Document.document_message_id == Message.message_id)
            .where(Message.message_conversation_id == conversation_id)
            .where(Document.document_mime_type.like(f"{file_type}%"))
            .order_by(desc(Document.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def search_documents(
        self,
        conversation_id: str,
        query: str,
        file_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Document]:
        """Search documents by filename"""
        stmt = (
            select(Document)
            .join(Message, Document.document_message_id == Message.message_id)
            .where(Message.message_conversation_id == conversation_id)
            .where(Document.document_filename.ilike(f"%{query}%"))
        )
        
        if file_type:
            stmt = stmt.where(Document.document_mime_type.like(f"{file_type}%"))
        
        stmt = (
            stmt.order_by(desc(Document.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def count_by_conversation(self, conversation_id: str) -> int:
        """Count documents in a conversation"""
        stmt = (
            select(func.count(Document.document_id))
            .join(Message, Document.document_message_id == Message.message_id)
            .where(Message.message_conversation_id == conversation_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def get_total_file_size(self, conversation_id: str) -> int:
        """Get total file size for a conversation"""
        stmt = (
            select(func.sum(Document.document_file_size))
            .join(Message, Document.document_message_id == Message.message_id)
            .where(Message.message_conversation_id == conversation_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

class MemoryHistoryRepository(AsyncBaseRepository[MemoryHistory]):
    """Repository for MemoryHistory operations - simplified for existing schema"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, MemoryHistory)
    
    async def get_by_conversation(
        self,
        conversation_id: str,
        memory_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[MemoryHistory]:
        """Get memory entries by conversation"""
        stmt = select(MemoryHistory).where(MemoryHistory.conversation_id == conversation_id)
        
        # Since we only have date_time and memory_history columns, we'll filter by content if memory_type is specified
        if memory_type:
            # Filter by JSON content that contains the memory_type
            stmt = stmt.where(MemoryHistory.memory_history.ilike(f'%"type":"{memory_type}"%'))
        
        stmt = (
            stmt.order_by(desc(MemoryHistory.date_time))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_key(self, conversation_id: str, memory_key: str) -> Optional[MemoryHistory]:
        """Get memory by conversation and key (search in JSON content)"""
        stmt = (
            select(MemoryHistory)
            .where(MemoryHistory.conversation_id == conversation_id)
            .where(MemoryHistory.memory_history.ilike(f'%"key":"{memory_key}"%'))
            .order_by(desc(MemoryHistory.date_time))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def search_memories(
        self,
        conversation_id: str,
        query: str,
        memory_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[MemoryHistory]:
        """Search memories by content"""
        stmt = (
            select(MemoryHistory)
            .where(MemoryHistory.conversation_id == conversation_id)
            .where(MemoryHistory.memory_history.ilike(f"%{query}%"))
        )
        
        if memory_type:
            stmt = stmt.where(MemoryHistory.memory_history.ilike(f'%"type":"{memory_type}"%'))
        
        stmt = (
            stmt.order_by(desc(MemoryHistory.date_time))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_high_priority_memories(
        self,
        conversation_id: str,
        min_priority: int = 5,
        limit: int = 20
    ) -> List[MemoryHistory]:
        """Get high priority memories (filter by JSON content)"""
        stmt = (
            select(MemoryHistory)
            .where(MemoryHistory.conversation_id == conversation_id)
            .where(MemoryHistory.memory_history.ilike(f'%"priority":%'))
            .order_by(desc(MemoryHistory.date_time))
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        memories = list(result.scalars().all())
        
        # Filter by priority in Python since we can't do complex JSON queries easily
        filtered_memories = []
        for memory in memories:
            if memory.priority >= min_priority:
                filtered_memories.append(memory)
                if len(filtered_memories) >= limit:
                    break
        
        return filtered_memories
    
    async def cleanup_expired_memories(self) -> int:
        """Remove expired memories (implemented in Python since expires_at is in JSON)"""
        stmt = select(MemoryHistory)
        result = await self.session.execute(stmt)
        all_memories = list(result.scalars().all())
        
        deleted_count = 0
        current_time = datetime.utcnow()
        
        for memory in all_memories:
            expires_at = memory.expires_at
            if expires_at and expires_at <= current_time:
                await self.session.delete(memory)
                deleted_count += 1
        
        if deleted_count > 0:
            await self.session.flush()
        
        return deleted_count
    
    async def count_by_conversation(self, conversation_id: str, memory_type: Optional[str] = None) -> int:
        """Count memories in a conversation"""
        stmt = select(func.count(MemoryHistory.id)).where(MemoryHistory.conversation_id == conversation_id)
        
        if memory_type:
            stmt = stmt.where(MemoryHistory.memory_history.ilike(f'%"type":"{memory_type}"%'))
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def upsert_memory(
        self,
        conversation_id: str,
        memory_key: str,
        memory_value: str,
        memory_type: str = "context",
        priority: int = 1,
        expires_at: Optional[datetime] = None
    ) -> MemoryHistory:
        """Insert or update memory entry using simplified schema"""
        # Try to find existing memory by key
        existing = await self.get_by_key(conversation_id, memory_key)
        
        if existing:
            # Update existing memory with new structured data
            existing.set_structured_memory(memory_key, memory_value, memory_type, priority, expires_at)
            updated_memory = await self.save(existing)
            await self.session.flush()
            return updated_memory
        else:
            # Create new memory with structured data
            new_memory = MemoryHistory(
                conversation_id=conversation_id,
                date_time=datetime.utcnow()
            )
            new_memory.set_structured_memory(memory_key, memory_value, memory_type, priority, expires_at)
            return await self.save(new_memory)

__all__ = [
    "MessageRepository",
    "DocumentRepository",  
    "MemoryHistoryRepository"
]