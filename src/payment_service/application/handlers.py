"""Обработчики команд."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from payment_service.domain.enums import PaymentStatus
from payment_service.domain.models import Payment
from payment_service.infrastructure.gateway import emulate_processing

if TYPE_CHECKING:
    from uuid import UUID

    from payment_service.application.commands import CreatePayment, GetPayment, ProcessPayment
    from payment_service.application.uow import UnitOfWork


class PaymentNotFoundError(Exception):
    """Платёж не найден."""

    def __init__(self, payment_id: UUID) -> None:
        """Запомнить id ненайденного платежа."""
        super().__init__(payment_id)

        self.payment_id = payment_id


async def create_payment(command: CreatePayment, uow: UnitOfWork) -> Payment:
    """Создать платёж и событие в outbox одной транзакцией."""
    payment = Payment(
        amount=command.amount,
        currency=command.currency,
        description=command.description,
        meta=command.meta,
        webhook_url=command.webhook_url,
        idempotency_key=command.idempotency_key,
    )

    async with uow:
        if not await uow.payments.add_if_absent(payment):
            existing = await uow.payments.get_by_idempotency_key(command.idempotency_key)
            if existing is None:
                msg = 'Платёж не найден после конфликта по idempotency key'
                raise RuntimeError(msg)

            return existing

        await uow.outbox.add('payment.created', {'payment_id': str(payment.id)})
        await uow.commit()

        return payment


async def get_payment(command: GetPayment, uow: UnitOfWork) -> Payment:
    """Вернуть платёж по id."""
    async with uow:
        payment = await uow.payments.get(command.payment_id)
        if payment is None:
            raise PaymentNotFoundError(command.payment_id)

        return payment


async def process_payment(command: ProcessPayment, uow: UnitOfWork) -> Payment:
    """Провести платёж через эмуляцию шлюза и обновить статус."""
    async with uow:
        payment = await uow.payments.get(command.payment_id)
        if payment is None:
            raise PaymentNotFoundError(command.payment_id)
        if payment.status is not PaymentStatus.PENDING:
            return payment

        success = await emulate_processing()
        payment.status = PaymentStatus.SUCCEEDED if success else PaymentStatus.FAILED
        payment.processed_at = datetime.now(UTC)

        await uow.payments.update(payment)
        await uow.commit()

        return payment
