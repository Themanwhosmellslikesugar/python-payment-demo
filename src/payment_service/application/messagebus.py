"""Шина сообщений."""

from __future__ import annotations

from typing import TYPE_CHECKING

from payment_service.application import commands, handlers

if TYPE_CHECKING:
    from payment_service.application.uow import UnitOfWork
    from payment_service.domain.models import Payment


class MessageBus:
    """Диспетчер команд к обработчикам."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Запомнить UnitOfWork."""
        self._uow = uow

    async def handle(self, message: commands.Command) -> Payment:
        """Передать команду нужному обработчику."""
        match message:
            case commands.CreatePayment():
                return await handlers.create_payment(message, self._uow)
            case commands.GetPayment():
                return await handlers.get_payment(message, self._uow)
            case commands.ProcessPayment():
                return await handlers.process_payment(message, self._uow)
