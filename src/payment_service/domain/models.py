"""Доменные модели."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

if TYPE_CHECKING:
    from decimal import Decimal
    from uuid import UUID

from payment_service.domain.enums import Currency, PaymentStatus


@dataclass
class Payment:
    """Платёж."""

    amount: Decimal
    currency: Currency
    description: str
    meta: dict[str, Any]
    webhook_url: str
    idempotency_key: str
    id: UUID = field(default_factory=uuid4)
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    processed_at: datetime | None = None
