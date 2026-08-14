"""Репозитории."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from payment_service.domain.models import Payment
from payment_service.infrastructure.db.tables import OutboxTable, PaymentTable

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


class PaymentRepository:
    """Доступ к таблице payments."""

    def __init__(self, session: AsyncSession) -> None:
        """Запомнить сессию."""
        self._session = session

    async def add(self, payment: Payment) -> None:
        """Сохранить новый платёж."""
        self._session.add(self._to_table(payment))

    async def get(self, payment_id: UUID) -> Payment | None:
        """Найти платёж по id."""
        row = await self._session.get(PaymentTable, payment_id)
        return self._to_domain(row) if row is not None else None

    async def get_by_idempotency_key(self, key: str) -> Payment | None:
        """Найти платёж по idempotency key."""
        stmt = select(PaymentTable).where(PaymentTable.idempotency_key == key)
        row = await self._session.scalar(stmt)
        return self._to_domain(row) if row is not None else None

    @staticmethod
    def _to_domain(row: PaymentTable) -> Payment:
        return Payment(
            id=row.id,
            amount=row.amount,
            currency=row.currency,
            description=row.description,
            meta=row.meta,
            webhook_url=row.webhook_url,
            idempotency_key=row.idempotency_key,
            status=row.status,
            created_at=row.created_at,
            processed_at=row.processed_at,
        )

    @staticmethod
    def _to_table(payment: Payment) -> PaymentTable:
        return PaymentTable(
            id=payment.id,
            amount=payment.amount,
            currency=payment.currency,
            description=payment.description,
            meta=payment.meta,
            webhook_url=payment.webhook_url,
            idempotency_key=payment.idempotency_key,
            status=payment.status,
            created_at=payment.created_at,
            processed_at=payment.processed_at,
        )


class OutboxRepository:
    """Доступ к таблице outbox."""

    def __init__(self, session: AsyncSession) -> None:
        """Запомнить сессию."""
        self._session = session

    async def add(self, event_type: str, payload: dict[str, Any]) -> None:
        """Добавить событие в outbox."""
        row = OutboxTable(event_type=event_type, payload=payload, created_at=datetime.now(UTC))
        self._session.add(row)
