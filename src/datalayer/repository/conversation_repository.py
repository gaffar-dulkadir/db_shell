"""
Conversation Repository for Chat Marketplace Service
Handles Conversation operations with related entities
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, update, delete, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from ._base_repository import AsyncBaseRepository
from ..model.sqlalchemy_models import Conversation, Message, User, Bot
from ..model.dto.chat_dto import ConversationStatus

class ConversationRepository(AsyncBaseRepository[Conversation]):
    """Repository for Conversation operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversation)
    
    async def get_by_user_id(
        self, 
        user_id: str, 
        limit: int = 20, 
        offset: int = 0,
        status: Optional[ConversationStatus] = None
    ) -> List[Conversation]:
        """Get conversations by user ID"""
        stmt = (
            select(Conversation)
            .where(Conversation.conversation_user_id == user_id)
        )
        
        if status:
            stmt = stmt.where(Conversation.conversation_status == status.value)
        
        stmt = (
            stmt.limit(limit)
            .offset(offset)
            .order_by(desc(Conversation.last_message_at), desc(Conversation.conversation_updated_at))
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_with_messages(
        self, 
        conversation_id: str, 
        message_limit: int = 50
    ) -> Optional[Conversation]:
        """Get conversation with recent messages"""
        # First get the conversation
        conversation_stmt = (
            select(Conversation)
            .options(selectinload(Conversation.bot))
            .where(Conversation.conversation_id == conversation_id)
        )
        conversation_result = await self.session.execute(conversation_stmt)
        conversation = conversation_result.scalar_one_or_none()
        
        if not conversation:
            return None
        
        # Then get recent messages
        messages_stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .where(Message.is_deleted == False)
            .order_by(desc(Message.created_at))
            .limit(message_limit)
        )
        messages_result = await self.session.execute(messages_stmt)
        messages = list(messages_result.scalars().all())
        
        # Reverse to get chronological order
        conversation.messages = list(reversed(messages))
        
        return conversation
    
    async def get_with_bot_info(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation with bot information"""
        stmt = (
            select(Conversation)
            .options(selectinload(Conversation.bot))
            .where(Conversation.conversation_id == conversation_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def search_conversations(
        self,
        user_id: str,
        query: str,
        status: Optional[ConversationStatus] = None,
        bot_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """Search conversations by title or description"""
        stmt = (
            select(Conversation)
            .where(Conversation.conversation_user_id == user_id)
            .where(
                or_(
                    Conversation.conversation_title.ilike(f"%{query}%"),
                    Conversation.conversation_title.ilike(f"%{query}%")  # No description field in DB
                )
            )
        )
        
        if status:
            stmt = stmt.where(Conversation.conversation_status == status.value)
        
        if bot_id:
            stmt = stmt.where(Conversation.conversation_bot_id == bot_id)
        
        stmt = (
            stmt.limit(limit)
            .offset(offset)
            .order_by(desc(Conversation.last_message_at), desc(Conversation.conversation_updated_at))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_bot_id(
        self, 
        bot_id: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Conversation]:
        """Get conversations by bot ID"""
        stmt = (
            select(Conversation)
            .where(Conversation.conversation_bot_id == bot_id)
            .where(Conversation.conversation_status == ConversationStatus.ACTIVE.value)
            .limit(limit)
            .offset(offset)
            .order_by(desc(Conversation.last_message_at))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def count_by_user(self, user_id: str, status: Optional[ConversationStatus] = None) -> int:
        """Count conversations by user"""
        stmt = select(func.count(Conversation.conversation_id)).where(Conversation.conversation_user_id == user_id)
        
        if status:
            stmt = stmt.where(Conversation.conversation_status == status.value)
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def count_by_bot(self, bot_id: str) -> int:
        """Count conversations by bot"""
        stmt = (
            select(func.count(Conversation.conversation_id))
            .where(Conversation.conversation_bot_id == bot_id)
            .where(Conversation.conversation_status == ConversationStatus.ACTIVE.value)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def update_last_message_time(self, conversation_id: str, message_time: datetime) -> bool:
        """Update conversation's last message timestamp"""
        stmt = (
            update(Conversation)
            .where(Conversation.conversation_id == conversation_id)
            .values(
                last_message_at=message_time,
                conversation_updated_at=datetime.utcnow()
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
    
    async def archive_conversation(self, conversation_id: str) -> bool:
        """Archive a conversation"""
        stmt = (
            update(Conversation)
            .where(Conversation.conversation_id == conversation_id)
            .values(
                conversation_status=ConversationStatus.ARCHIVED.value,
                conversation_updated_at=datetime.utcnow()
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
    
    async def restore_conversation(self, conversation_id: str) -> bool:
        """Restore an archived conversation"""
        stmt = (
            update(Conversation)
            .where(Conversation.conversation_id == conversation_id)
            .values(
                conversation_status=ConversationStatus.ACTIVE.value,
                conversation_updated_at=datetime.utcnow()
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Soft delete a conversation"""
        stmt = (
            update(Conversation)
            .where(Conversation.conversation_id == conversation_id)
            .values(
                conversation_status=ConversationStatus.DELETED.value,
                conversation_updated_at=datetime.utcnow()
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
    
    async def get_recent_conversations(
        self, 
        user_id: str, 
        days: int = 7, 
        limit: int = 10
    ) -> List[Conversation]:
        """Get recent conversations within specified days"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        stmt = (
            select(Conversation)
            .where(Conversation.conversation_user_id == user_id)
            .where(Conversation.conversation_status == ConversationStatus.ACTIVE.value)
            .where(Conversation.last_message_at >= since_date)
            .limit(limit)
            .order_by(desc(Conversation.last_message_at))
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_conversation_stats(self, user_id: str) -> Dict[str, Any]:
        """Get conversation statistics for a user"""
        total_stmt = select(func.count(Conversation.conversation_id)).where(Conversation.conversation_user_id == user_id)
        active_stmt = (
            select(func.count(Conversation.conversation_id))
            .where(Conversation.conversation_user_id == user_id)
            .where(Conversation.conversation_status == ConversationStatus.ACTIVE.value)
        )
        archived_stmt = (
            select(func.count(Conversation.conversation_id))
            .where(Conversation.conversation_user_id == user_id)
            .where(Conversation.conversation_status == ConversationStatus.ARCHIVED.value)
        )
        
        # Recent conversations (last 30 days)
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_stmt = (
            select(func.count(Conversation.conversation_id))
            .where(Conversation.conversation_user_id == user_id)
            .where(Conversation.conversation_created_at >= recent_date)
        )
        
        total_result = await self.session.execute(total_stmt)
        active_result = await self.session.execute(active_stmt)
        archived_result = await self.session.execute(archived_stmt)
        recent_result = await self.session.execute(recent_stmt)
        
        return {
            "total_conversations": total_result.scalar() or 0,
            "active_conversations": active_result.scalar() or 0,
            "archived_conversations": archived_result.scalar() or 0,
            "recent_conversations": recent_result.scalar() or 0,
        }
    
    async def get_conversations_with_message_count(
        self, 
        user_id: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get conversations with message count"""
        stmt = (
            select(
                Conversation,
                func.count(Message.message_id).label('message_count')
            )
            .outerjoin(Message, Conversation.conversation_id == Message.message_conversation_id)
            .where(Conversation.conversation_user_id == user_id)
            .group_by(Conversation.conversation_id)
            .limit(limit)
            .offset(offset)
            .order_by(desc(Conversation.last_message_at))
        )
        
        result = await self.session.execute(stmt)
        conversations_with_count = []
        
        for row in result:
            conversation = row[0]
            message_count = row[1] or 0
            conversations_with_count.append({
                "conversation": conversation,
                "message_count": message_count
            })
        
        return conversations_with_count

__all__ = ["ConversationRepository"]