"""Эндпоинты платежей."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from payment_service.api.deps import BusDep
from payment_service.api.schemas import (
    PaymentAcceptedResponse,
    PaymentCreateRequest,
    PaymentDetailResponse,
)
from payment_service.application.commands import CreatePayment, GetPayment
from payment_service.application.handlers import PaymentNotFoundError
from payment_service.domain.models import Payment

router = APIRouter(prefix='/api/v1', tags=['payments'])


@router.post('/payments', status_code=status.HTTP_202_ACCEPTED)
async def create_payment(
    body: PaymentCreateRequest,
    bus: BusDep,
    idempotency_key: Annotated[str, Header()],
) -> PaymentAcceptedResponse:
    """Принять платёж в обработку (идемпотентно по Idempotency-Key)."""
    payment: Payment = await bus.handle(
        CreatePayment(
            amount=body.amount,
            currency=body.currency,
            description=body.description,
            meta=body.meta,
            webhook_url=str(body.webhook_url),
            idempotency_key=idempotency_key,
        )
    )
    return PaymentAcceptedResponse(
        payment_id=payment.id,
        status=payment.status,
        created_at=payment.created_at,
    )


@router.get('/payments/{payment_id}')
async def get_payment(payment_id: UUID, bus: BusDep) -> PaymentDetailResponse:
    """Вернуть детальную информацию о платеже."""
    try:
        payment: Payment = await bus.handle(GetPayment(payment_id=payment_id))
    except PaymentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Платёж не найден',
        ) from None

    return PaymentDetailResponse(
        payment_id=payment.id,
        amount=payment.amount,
        currency=payment.currency,
        description=payment.description,
        metadata=payment.meta,
        status=payment.status,
        idempotency_key=payment.idempotency_key,
        webhook_url=payment.webhook_url,
        created_at=payment.created_at,
        processed_at=payment.processed_at,
    )
