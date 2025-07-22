"""Create item table

Revision ID: 006
Revises: 005
Create Date: 2025-01-22 10:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create items table
    op.create_table('items',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('item_type', sa.String(length=50), nullable=False),
        sa.Column('name_i18n_key', sa.String(length=100), nullable=False),
        sa.Column('description_i18n_key', sa.String(length=100), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('quality', sa.Float(), nullable=False),
        sa.Column('base_value', sa.Integer(), nullable=False),
        sa.Column('current_value', sa.Integer(), nullable=False),
        sa.Column('created_from_livestock_id', sa.String(length=36), nullable=True),
        sa.Column('custom_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_from_livestock_id'], ['livestock.id'], ),
        sa.ForeignKeyConstraint(['owner_id'], ['players.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_items_id'), 'items', ['id'], unique=False)
    op.create_index(op.f('ix_items_item_type'), 'items', ['item_type'], unique=False)
    op.create_index(op.f('ix_items_owner_id'), 'items', ['owner_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_items_owner_id'), table_name='items')
    op.drop_index(op.f('ix_items_item_type'), table_name='items')
    op.drop_index(op.f('ix_items_id'), table_name='items')
    op.drop_table('items')