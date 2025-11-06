"""Fix message schema - add user_id and message_type fields

Revision ID: fix_message_schema
Revises: add_bot_category_fields
Create Date: 2025-11-06 20:58:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'fix_message_schema'
down_revision = 'add_bot_category_fields'
branch_labels = None
depends_on = None

def upgrade():
    """Add missing fields to message table"""
    # Add message_user_id field for user messages
    op.add_column('message', 
        sa.Column('message_user_id', 
                 UUID(as_uuid=False), 
                 sa.ForeignKey('auth.users.user_id', ondelete='CASCADE'),
                 nullable=True,
                 comment='User ID for user messages'
        ),
        schema='chats'
    )
    
    # Add message_type field to store actual message type
    op.add_column('message',
        sa.Column('message_type',
                 sa.String(20),
                 nullable=False,
                 server_default='text',
                 comment='Type of message: text, image, document, etc.'
        ),
        schema='chats'
    )
    
    # Add index on message_user_id for performance
    op.create_index('ix_message_user_id', 'message', ['message_user_id'], schema='chats')
    
    # Add index on message_type for filtering
    op.create_index('ix_message_type', 'message', ['message_type'], schema='chats')

def downgrade():
    """Remove the added fields"""
    # Drop indexes
    op.drop_index('ix_message_type', 'message', schema='chats')
    op.drop_index('ix_message_user_id', 'message', schema='chats')
    
    # Drop columns
    op.drop_column('message', 'message_type', schema='chats')
    op.drop_column('message', 'message_user_id', schema='chats')