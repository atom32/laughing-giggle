"""Add livestock module constraint

Revision ID: 007
Revises: 006
Create Date: 2025-01-22 10:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add foreign key constraint from livestock to player_modules
    op.create_foreign_key(
        'fk_livestock_current_location_module_id', 
        'livestock', 
        'player_modules', 
        ['current_location_module_id'], 
        ['id']
    )


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_livestock_current_location_module_id', 'livestock', type_='foreignkey')