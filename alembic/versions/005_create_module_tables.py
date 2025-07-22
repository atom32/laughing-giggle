"""Create module tables

Revision ID: 005
Revises: 004
Create Date: 2025-01-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create player_modules table
    op.create_table('player_modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('module_type', sa.String(length=50), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('config_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_player_modules_id'), 'player_modules', ['id'], unique=False)
    op.create_index(op.f('ix_player_modules_module_type'), 'player_modules', ['module_type'], unique=False)
    op.create_index(op.f('ix_player_modules_player_id'), 'player_modules', ['player_id'], unique=False)

    # Create module_configs table
    op.create_table('module_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_type', sa.String(length=50), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('name_i18n_key', sa.String(length=100), nullable=False),
        sa.Column('description_i18n_key', sa.String(length=100), nullable=False),
        sa.Column('upgrade_cost', sa.Integer(), nullable=False),
        sa.Column('effects', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_module_configs_id'), 'module_configs', ['id'], unique=False)
    op.create_index(op.f('ix_module_configs_level'), 'module_configs', ['level'], unique=False)
    op.create_index(op.f('ix_module_configs_module_type'), 'module_configs', ['module_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_module_configs_module_type'), table_name='module_configs')
    op.drop_index(op.f('ix_module_configs_level'), table_name='module_configs')
    op.drop_index(op.f('ix_module_configs_id'), table_name='module_configs')
    op.drop_table('module_configs')
    op.drop_index(op.f('ix_player_modules_player_id'), table_name='player_modules')
    op.drop_index(op.f('ix_player_modules_module_type'), table_name='player_modules')
    op.drop_index(op.f('ix_player_modules_id'), table_name='player_modules')
    op.drop_table('player_modules')