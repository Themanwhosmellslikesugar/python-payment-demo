"""Точка входа consumer'а платежей."""

import asyncio
import contextlib
import logging

import httpx
from faststream import FastStream
from faststream.exceptions import RejectMessage
from faststream.rabbit import (
    ExchangeType,
    QueueType,
    RabbitBroker,
    RabbitExchange,
    RabbitMessage,
    RabbitQueue,
)
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from payment_service.application.commands import ProcessPayment
from payment_service.application.messagebus import MessageBus
from payment_service.application.uow import UnitOfWork
from payment_service.config import get_settings
from payment_service.consumer.publisher import QUEUE_NEW_PAYMENTS, publish_pending
from payment_service.consumer.schemas import PaymentCreatedMessage
from payment_service.infrastructure.webhook import WebhookSender

logger = logging.getLogger(__name__)

settings = get_settings()
engine = create_async_engine(settings.database_url)
session_factory = async_sessionmaker(engine, expire_on_commit=False)

broker = RabbitBroker(settings.rabbitmq_url)
app = FastStream(broker)

dlx = RabbitExchange('payments.dlx', type=ExchangeType.DIRECT, durable=True)
dlq = RabbitQueue('payments.dlq', durable=True)
new_payments_queue = RabbitQueue(
    QUEUE_NEW_PAYMENTS,
    queue_type=QueueType.QUORUM,
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'payments.dlx',
        'x-dead-letter-routing-key': 'payments.dlq',
    },
)

webhook_sender = WebhookSender(attempts=settings.webhook_retry_attempts)


@broker.subscriber(new_payments_queue)
async def process_new_payment(message: PaymentCreatedMessage, raw: RabbitMessage) -> None:
    """Обработать новый платёж и отправить webhook."""
    async with UnitOfWork(session_factory) as uow:
        payment = await MessageBus(uow).handle(ProcessPayment(payment_id=message.payment_id))

    try:
        await webhook_sender.send(payment)
    except httpx.HTTPError as exc:
        retries = int(raw.headers.get('x-retry-count', 0))
        if retries + 1 >= settings.consumer_max_attempts:
            raise RejectMessage from exc
        await broker.publish(
            {'payment_id': str(message.payment_id)},
            queue=QUEUE_NEW_PAYMENTS,
            headers={'x-retry-count': retries + 1},
            persist=True,
        )


@broker.subscriber(dlq, dlx)
async def handle_dead_letter(message: PaymentCreatedMessage) -> None:
    """Залогировать сообщение, попавшее в DLQ."""
    logger.error('Платёж %s не обработан после всех попыток, сообщение в DLQ', message.payment_id)


_publisher_task: asyncio.Task[None] | None = None


@app.after_startup
async def start_publisher() -> None:
    """Запустить фоновую публикацию событий из outbox."""
    global _publisher_task  # noqa: PLW0603
    _publisher_task = asyncio.create_task(
        publish_pending(broker, session_factory, settings.outbox_poll_interval)
    )


@app.on_shutdown
async def stop_publisher() -> None:
    """Остановить паблишер и закрыть пул соединений."""
    global _publisher_task  # noqa: PLW0603
    if _publisher_task is not None:
        _publisher_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await _publisher_task
        _publisher_task = None
    await engine.dispose()


def main() -> None:
    """Запустить consumer."""
    asyncio.run(app.run())


if __name__ == '__main__':
    main()
