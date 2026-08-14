"""Pydantic-схемы API."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from payment_service.domain.enums import Currency, PaymentStatus


class PaymentCreateRequest(BaseModel):
    """Тело запроса на создание платежа."""

    model_config = ConfigDict(populate_by_name=True)

    amount: Decimal = Field(gt=0, decimal_places=2)
    currency: Currency
    description: str = Field(min_length=1, max_length=1000)
    meta: dict[str, Any] = Field(default_factory=dict, alias='metadata')
    webhook_url: HttpUrl


class PaymentAcceptedResponse(BaseModel):
    """Ответ на создание платежа (202)."""

    payment_id: UUID
    status: PaymentStatus
    created_at: datetime


class PaymentDetailResponse(BaseModel):
    """Детальная информация о платеже."""

    payment_id: UUID
    amount: Decimal
    currency: Currency
    description: str
    metadata: dict[str, Any]
    status: PaymentStatus
    idempotency_key: str
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None
