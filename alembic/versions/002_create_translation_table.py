"""Create translation table

Revision ID: 002
Revises: 001
Create Date: 2025-07-22 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create translation table for internationalization support."""
    op.create_table(
        'translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('language_code', sa.String(length=10), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_translations'),
        sa.UniqueConstraint('key', 'language_code', name='uq_translation_key_language')
    )
    
    # Create indexes for efficient lookups
    op.create_index('ix_translations_id', 'translations', ['id'], unique=False)
    op.create_index('ix_translations_key', 'translations', ['key'], unique=False)
    op.create_index('ix_translations_language_code', 'translations', ['language_code'], unique=False)
    op.create_index('ix_translations_category', 'translations', ['category'], unique=False)


def downgrade() -> None:
    """Drop translation table."""
    op.drop_index('ix_translations_category', table_name='translations')
    op.drop_index('ix_translations_language_code', table_name='translations')
    op.drop_index('ix_translations_key', table_name='translations')
    op.drop_index('ix_translations_id', table_name='translations')
    op.drop_table('translations')