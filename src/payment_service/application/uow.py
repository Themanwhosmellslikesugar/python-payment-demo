"""UnitOfWork."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from payment_service.application.repositories import OutboxRepository, PaymentRepository

if TYPE_CHECKING:
    from types import TracebackType

    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class UnitOfWork:
    """Атомарная единица работы с БД."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """Запомнить фабрику сессий."""
        self._session_factory = session_factory

    async def __aenter__(self) -> Self:
        """Открыть сессию и репозитории."""
        self.session = self._session_factory()
        self.payments = PaymentRepository(self.session)
        self.outbox = OutboxRepository(self.session)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Откатить и закрыть сессию."""
        await self.rollback()
        await self.session.close()

    async def commit(self) -> None:
        """Зафиксировать транзакцию."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Откатить транзакцию."""
        await self.session.rollback()
