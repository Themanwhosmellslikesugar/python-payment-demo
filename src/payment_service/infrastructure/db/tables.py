"""ORM-таблицы."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, Enum, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from payment_service.domain.enums import Currency, PaymentStatus
from payment_service.infrastructure.db.base import Base


class PaymentTable(Base):
    """Таблица payments."""

    __tablename__ = 'payments'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[Currency] = mapped_column(
        Enum(
            Currency,
            native_enum=False,
            create_constraint=True,
            name='ck_payments_currency',
            values_callable=lambda x: [item.value for item in x],
            length=None,
            inherit_schema=True,
        ),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text)
    meta: Mapped[dict[str, Any]] = mapped_column('metadata', JSONB)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(
            PaymentStatus,
            native_enum=False,
            create_constraint=True,
            name='ck_payments_status',
            values_callable=lambda x: [item.value for item in x],
            length=None,
            inherit_schema=True,
        ),
        nullable=False,
        default=PaymentStatus.PENDING,
    )
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    webhook_url: Mapped[str] = mapped_column(String(2048))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class OutboxTable(Base):
    """Таблица outbox."""

    __tablename__ = 'outbox'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(255))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
