"""Обработчики команд."""

from __future__ import annotations

from typing import TYPE_CHECKING

from payment_service.domain.models import Payment

if TYPE_CHECKING:
    from uuid import UUID

    from payment_service.application.commands import CreatePayment, GetPayment
    from payment_service.application.uow import UnitOfWork


class PaymentNotFoundError(Exception):
    """Платёж не найден."""

    def __init__(self, payment_id: UUID) -> None:
        """Запомнить id ненайденного платежа."""
        super().__init__(payment_id)

        self.payment_id = payment_id


async def create_payment(command: CreatePayment, uow: UnitOfWork) -> Payment:
    """Создать платёж и событие в outbox одной транзакцией."""
    async with uow:
        existing = await uow.payments.get_by_idempotency_key(command.idempotency_key)
        if existing is not None:
            return existing

        payment = Payment(
            amount=command.amount,
            currency=command.currency,
            description=command.description,
            meta=command.meta,
            webhook_url=command.webhook_url,
            idempotency_key=command.idempotency_key,
        )

        await uow.payments.add(payment)
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
