"""Create livestock table

Revision ID: 004
Revises: 003
Create Date: 2025-01-22 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create livestock table
    op.create_table('livestock',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('name_i18n_key', sa.String(length=100), nullable=False),
        sa.Column('family_i18n_key', sa.String(length=100), nullable=False),
        sa.Column('nation_i18n_key', sa.String(length=100), nullable=False),
        sa.Column('city_i18n_key', sa.String(length=100), nullable=False),
        sa.Column('pic_url', sa.String(length=255), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('bloodtype_i18n_key', sa.String(length=50), nullable=False),
        sa.Column('zodiac_i18n_key', sa.String(length=50), nullable=False),
        sa.Column('origin_i18n_key', sa.String(length=100), nullable=False),
        sa.Column('rank_i18n_key', sa.String(length=50), nullable=False),
        sa.Column('acquire_turn', sa.Integer(), nullable=False),
        sa.Column('quality', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('height', sa.Float(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('father_id', sa.String(length=36), nullable=True),
        sa.Column('mother_id', sa.String(length=36), nullable=True),
        sa.Column('current_location_module_id', sa.Integer(), nullable=True),
        sa.Column('custom_data', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_livestock_id'), 'livestock', ['id'], unique=False)
    op.create_index(op.f('ix_livestock_owner_id'), 'livestock', ['owner_id'], unique=False)
    
    # Create foreign key constraints
    op.create_foreign_key(None, 'livestock', 'players', ['owner_id'], ['id'])
    op.create_foreign_key(None, 'livestock', 'livestock', ['father_id'], ['id'])
    op.create_foreign_key(None, 'livestock', 'livestock', ['mother_id'], ['id'])
    # Note: Foreign key to player_modules is added in migration 007


def downgrade() -> None:
    # Drop foreign key constraints
    op.drop_constraint(None, 'livestock', type_='foreignkey')
    
    # Drop indexes
    op.drop_index(op.f('ix_livestock_owner_id'), table_name='livestock')
    op.drop_index(op.f('ix_livestock_id'), table_name='livestock')
    
    # Drop table
    op.drop_table('livestock')