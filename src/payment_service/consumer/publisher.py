"""Паблишер событий из outbox в RabbitMQ."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from payment_service.application.uow import UnitOfWork

if TYPE_CHECKING:
    from faststream.rabbit import RabbitBroker
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

QUEUE_NEW_PAYMENTS = 'payments.new'


async def publish_pending(
    broker: RabbitBroker,
    session_factory: async_sessionmaker[AsyncSession],
    poll_interval: float,
) -> None:
    """Публиковать неотправленные события из outbox."""
    while True:
        async with UnitOfWork(session_factory) as uow:
            events = await uow.outbox.fetch_unsent()
            for event in events:
                await broker.publish(event.payload, queue=QUEUE_NEW_PAYMENTS, persist=True)
                await uow.outbox.mark_sent(event.id)
            await uow.commit()
        await asyncio.sleep(poll_interval)
