"""phase6_custody_events

Revision ID: e73c891a54b2
Revises: d91a82f3a4e1
Create Date: 2026-09-23 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e73c891a54b2'
down_revision: Union[str, Sequence[str], None] = 'e72b94a1c5d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with Phase 6 custody_events table."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'custody_events' not in tables:
        op.create_table(
            'custody_events',
            sa.Column('id', sa.String(length=64), primary_key=True),
            sa.Column('evidence_id', sa.String(length=64), sa.ForeignKey('evidence_records.id', ondelete='CASCADE'), nullable=False),
            sa.Column('session_id', sa.String(length=64), sa.ForeignKey('test_sessions.id', ondelete='CASCADE'), nullable=False),
            sa.Column('sender_operator_id', sa.String(length=64), nullable=False),
            sa.Column('receiver_name', sa.String(length=128), nullable=False),
            sa.Column('receiver_agency', sa.String(length=128), nullable=False),
            sa.Column('receiver_badge_or_id', sa.String(length=64), nullable=False),
            sa.Column('package_seal_verified', sa.Boolean(), default=True, nullable=False),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('transferred_at_utc', sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index(op.f('ix_custody_events_id'), 'custody_events', ['id'], unique=False)
        op.create_index(op.f('ix_custody_events_evidence_id'), 'custody_events', ['evidence_id'], unique=False)
        op.create_index(op.f('ix_custody_events_session_id'), 'custody_events', ['session_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_custody_events_session_id'), table_name='custody_events')
    op.drop_index(op.f('ix_custody_events_evidence_id'), table_name='custody_events')
    op.drop_index(op.f('ix_custody_events_id'), table_name='custody_events')
    op.drop_table('custody_events')
