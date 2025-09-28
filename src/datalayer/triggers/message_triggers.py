"""
Message Triggers for Chat Marketplace Service
Implements the chats.set_parent_message() functionality using SQLAlchemy events
"""

import logging
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from datalayer.model.sqlalchemy_models import Message

logger = logging.getLogger(__name__)

async def set_parent_message_trigger(session: AsyncSession, message: Message) -> None:
    """
    Trigger function to set parent_message_id for new messages.
    This implements the chats.set_parent_message() functionality.
    
    Args:
        session: Database session
        message: The message being inserted
    """
    try:
        # Only set parent if not already set and message has a conversation
        if message.parent_message_id is None and message.conversation_id:
            # Get the last message in the same conversation
            stmt = (
                select(Message.message_id)
                .where(Message.conversation_id == message.conversation_id)
                .where(Message.message_id != message.message_id)  # Exclude current message
                .where(Message.is_deleted == False)
                .order_by(Message.created_at.desc())
                .limit(1)
            )
            
            result = await session.execute(stmt)
            last_message_id = result.scalar_one_or_none()
            
            if last_message_id:
                message.parent_message_id = last_message_id
                logger.debug(f"Set parent_message_id for message {message.message_id}: {last_message_id}")
            else:
                logger.debug(f"No parent message found for message {message.message_id} in conversation {message.conversation_id}")
                
    except Exception as e:
        logger.error(f"Error in set_parent_message_trigger: {e}")
        # Don't raise exception to avoid breaking the insert operation
        pass

@event.listens_for(Message, 'before_insert')
def message_before_insert_listener(mapper, connection, target):
    """
    Synchronous event listener for message before insert.
    This will be called before any message is inserted.
    """
    logger.debug(f"Message before_insert event triggered for message in conversation: {target.conversation_id}")

@event.listens_for(Message, 'after_insert')
def message_after_insert_listener(mapper, connection, target):
    """
    Synchronous event listener for message after insert.
    This handles post-insert operations.
    """
    logger.debug(f"Message after_insert event triggered for message: {target.message_id}")

# Alternative implementation using SQLAlchemy's session events for async support
@event.listens_for(Session, 'before_flush')
def session_before_flush_listener(session, flush_context, instances):
    """
    Session-level event listener to handle parent message setting before flush.
    This allows us to work with async sessions properly.
    """
    try:
        # Find new messages that need parent message setting
        new_messages = [obj for obj in session.new if isinstance(obj, Message)]
        
        for message in new_messages:
            if message.parent_message_id is None and message.conversation_id:
                # We'll set a flag to handle this in after_flush
                message._needs_parent_update = True
                logger.debug(f"Marked message {message.message_id} for parent update")
                
    except Exception as e:
        logger.error(f"Error in session_before_flush_listener: {e}")

@event.listens_for(Session, 'after_flush')
def session_after_flush_listener(session, flush_context):
    """
    Session-level event listener to handle parent message setting after flush.
    This runs after the messages are inserted and have IDs.
    """
    import asyncio
    
    try:
        # Find messages that need parent updates
        messages_to_update = [
            obj for obj in session.new 
            if isinstance(obj, Message) and hasattr(obj, '_needs_parent_update')
        ]
        
        if messages_to_update:
            # Create async task to handle parent message updates
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, create a task
                task = loop.create_task(_update_parent_messages(session, messages_to_update))
                # Add callback to handle any errors
                task.add_done_callback(lambda t: logger.error(f"Parent message update error: {t.exception()}") if t.exception() else None)
            else:
                # If not in async context, run synchronously
                loop.run_until_complete(_update_parent_messages(session, messages_to_update))
                
    except Exception as e:
        logger.error(f"Error in session_after_flush_listener: {e}")

async def _update_parent_messages(session: AsyncSession, messages: list[Message]) -> None:
    """
    Helper function to update parent message IDs for a list of messages.
    
    Args:
        session: Database session
        messages: List of messages to update
    """
    try:
        for message in messages:
            if hasattr(message, '_needs_parent_update'):
                await set_parent_message_trigger(session, message)
                delattr(message, '_needs_parent_update')
        
        # Commit the parent message updates
        await session.commit()
        
    except Exception as e:
        logger.error(f"Error updating parent messages: {e}")
        await session.rollback()

# Manual trigger function that can be called from services
async def manually_set_parent_message(session: AsyncSession, message_id: str) -> bool:
    """
    Manually set parent message for a specific message.
    This can be called from services when needed.
    
    Args:
        session: Database session
        message_id: ID of the message to update
        
    Returns:
        bool: True if parent was set, False otherwise
    """
    try:
        # Get the message
        message_stmt = select(Message).where(Message.message_id == message_id)
        message_result = await session.execute(message_stmt)
        message = message_result.scalar_one_or_none()
        
        if not message:
            logger.warning(f"Message not found: {message_id}")
            return False
        
        # Set parent message
        await set_parent_message_trigger(session, message)
        
        # Save changes
        await session.commit()
        
        logger.info(f"Successfully set parent message for: {message_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error manually setting parent message: {e}")
        await session.rollback()
        return False

# Function to validate parent message relationships
async def validate_parent_message_chain(session: AsyncSession, conversation_id: str) -> dict:
    """
    Validate and analyze parent message relationships in a conversation.
    
    Args:
        session: Database session
        conversation_id: ID of the conversation to validate
        
    Returns:
        dict: Validation results and statistics
    """
    try:
        # Get all messages in the conversation
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .where(Message.is_deleted == False)
            .order_by(Message.created_at.asc())
        )
        
        result = await session.execute(stmt)
        messages = list(result.scalars().all())
        
        if not messages:
            return {"valid": True, "message_count": 0, "chain_length": 0}
        
        # Analyze the chain
        total_messages = len(messages)
        messages_with_parent = sum(1 for msg in messages if msg.parent_message_id is not None)
        
        # First message should not have parent
        first_message = messages[0]
        first_message_valid = first_message.parent_message_id is None
        
        # Check for broken chains
        broken_chains = 0
        for msg in messages[1:]:  # Skip first message
            if msg.parent_message_id:
                # Check if parent exists in the conversation
                parent_exists = any(m.message_id == msg.parent_message_id for m in messages)
                if not parent_exists:
                    broken_chains += 1
        
        return {
            "valid": broken_chains == 0 and first_message_valid,
            "message_count": total_messages,
            "messages_with_parent": messages_with_parent,
            "broken_chains": broken_chains,
            "first_message_valid": first_message_valid,
            "chain_coverage": messages_with_parent / max(total_messages - 1, 1) * 100  # Exclude first message
        }
        
    except Exception as e:
        logger.error(f"Error validating parent message chain: {e}")
        return {"valid": False, "error": str(e)}

__all__ = [
    "set_parent_message_trigger",
    "manually_set_parent_message", 
    "validate_parent_message_chain"
]