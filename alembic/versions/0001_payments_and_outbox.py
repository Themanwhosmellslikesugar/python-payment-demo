"""Add payments и outbox.

Revision ID: 0001
Revises:
Create Date: 2026-08-14 06:55:21
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = '0001'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Создать таблицы payments и outbox."""
    op.create_table(
        'payments',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('idempotency_key', sa.String(255), nullable=False),
        sa.Column('webhook_url', sa.String(2048), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("currency IN ('RUB', 'USD', 'EUR')", name='ck_payments_currency'),
        sa.CheckConstraint(
            "status IN ('pending', 'succeeded', 'failed')", name='ck_payments_status'
        ),
    )
    op.create_index('ix_payments_idempotency_key', 'payments', ['idempotency_key'], unique=True)

    op.create_table(
        'outbox',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('event_type', sa.String(255), nullable=False),
        sa.Column('payload', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Удалить таблицы payments и outbox."""
    op.drop_table('outbox')
    op.drop_index('ix_payments_idempotency_key', table_name='payments')
    op.drop_table('payments')
