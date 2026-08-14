"""Схемы сообщений из очередей."""

from uuid import UUID

from pydantic import BaseModel


class PaymentCreatedMessage(BaseModel):
    """Сообщение о новом платеже из очереди payments.new."""

    payment_id: UUID
