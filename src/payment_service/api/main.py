"""Сборка FastAPI-приложения."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from payment_service.api.deps import verify_api_key
from payment_service.api.payments import router as payments_router
from payment_service.config import get_settings

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Пул соединений к БД на время жизни приложения."""
    engine = create_async_engine(get_settings().database_url)
    app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)
    yield
    await engine.dispose()


app = FastAPI(
    title='payment-service',
    lifespan=lifespan,
    dependencies=[Depends(verify_api_key)],
)
app.include_router(payments_router)
