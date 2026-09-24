"""phase5_procedural_context_enhancements

Revision ID: d91a82f3a4e1
Revises: cb280e8353a3
Create Date: 2026-09-23 15:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e72b94a1c5d2'
down_revision: Union[str, Sequence[str], None] = 'cb280e8353a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with Phase 5 procedural context enhancements."""
    op.add_column('procedural_context', sa.Column('kit_lot_number', sa.String(length=64), nullable=True))
    op.add_column('procedural_context', sa.Column('kit_expiry_date', sa.String(length=32), nullable=True))
    op.add_column('procedural_context', sa.Column('updated_at_utc', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('procedural_context', 'updated_at_utc')
    op.drop_column('procedural_context', 'kit_expiry_date')
    op.drop_column('procedural_context', 'kit_lot_number')
