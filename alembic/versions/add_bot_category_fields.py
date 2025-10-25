"""Add missing fields to bot_categories table

Revision ID: add_bot_category_fields
Revises: 
Create Date: 2025-01-25 16:34:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_bot_category_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add missing fields to bot_categories table
    op.add_column('bot_categories', 
                  sa.Column('icon', sa.String(500), nullable=True), 
                  schema='marketplace')
    op.add_column('bot_categories', 
                  sa.Column('color', sa.String(7), nullable=True), 
                  schema='marketplace')
    op.add_column('bot_categories', 
                  sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'), 
                  schema='marketplace')
    op.add_column('bot_categories', 
                  sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'), 
                  schema='marketplace')

def downgrade():
    # Remove added columns in reverse order
    op.drop_column('bot_categories', 'sort_order', schema='marketplace')
    op.drop_column('bot_categories', 'is_active', schema='marketplace')
    op.drop_column('bot_categories', 'color', schema='marketplace')
    op.drop_column('bot_categories', 'icon', schema='marketplace')