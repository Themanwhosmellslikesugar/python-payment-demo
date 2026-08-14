"""Отправка webhook-уведомлений."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

if TYPE_CHECKING:
    from payment_service.domain.models import Payment


class WebhookSender:
    """Отправка уведомлений с повторными попытками."""

    def __init__(self, attempts: int, timeout: float = 5.0) -> None:
        """Настроить число попыток и таймаут запроса."""
        self._attempts = attempts
        self._timeout = timeout

    async def send(self, payment: Payment) -> None:
        """Отправить уведомление с экспоненциальной задержкой между попытками."""
        retryer = AsyncRetrying(
            stop=stop_after_attempt(self._attempts),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(httpx.HTTPError),
            reraise=True,
        )
        await retryer(self._post, payment)

    async def _post(self, payment: Payment) -> None:
        payload: dict[str, Any] = {
            'payment_id': str(payment.id),
            'status': payment.status.value,
            'processed_at': payment.processed_at.isoformat() if payment.processed_at else None,
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(payment.webhook_url, json=payload)
            response.raise_for_status()
