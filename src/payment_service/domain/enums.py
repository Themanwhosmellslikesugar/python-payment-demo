"""Доменные перечисления."""

import enum


class Currency(enum.StrEnum):
    """Валюта платежа."""

    RUB = 'RUB'
    USD = 'USD'
    EUR = 'EUR'


class PaymentStatus(enum.StrEnum):
    """Статус платежа."""

    PENDING = 'pending'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
