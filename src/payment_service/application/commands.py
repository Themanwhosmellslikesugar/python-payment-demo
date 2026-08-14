"""Команды приложения."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from decimal import Decimal
    from uuid import UUID

    from payment_service.domain.enums import Currency


@dataclass(frozen=True)
class CreatePayment:
    """Создать платёж."""

    amount: Decimal
    currency: Currency
    description: str
    meta: dict[str, Any]
    webhook_url: str
    idempotency_key: str


@dataclass(frozen=True)
class GetPayment:
    """Получить платёж по id."""

    payment_id: UUID


type Command = CreatePayment | GetPayment
