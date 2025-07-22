"""Create player table

Revision ID: 003
Revises: 002
Create Date: 2025-01-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create players table
    op.create_table('players',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=False),
        sa.Column('birth_month', sa.Integer(), nullable=False),
        sa.Column('family_background', sa.String(length=100), nullable=False),
        sa.Column('childhood_experience', sa.String(length=100), nullable=False),
        sa.Column('education_background', sa.String(length=100), nullable=False),
        sa.Column('starting_city', sa.String(length=100), nullable=False),
        sa.Column('money', sa.Integer(), nullable=False, server_default='10000'),
        sa.Column('current_turn', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_played', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_players_id'), 'players', ['id'], unique=False)
    op.create_index(op.f('ix_players_user_id'), 'players', ['user_id'], unique=False)
    
    # Create foreign key constraint
    op.create_foreign_key(None, 'players', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint(None, 'players', type_='foreignkey')
    
    # Drop indexes
    op.drop_index(op.f('ix_players_user_id'), table_name='players')
    op.drop_index(op.f('ix_players_id'), table_name='players')
    
    # Drop table
    op.drop_table('players')