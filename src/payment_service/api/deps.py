"""Зависимости FastAPI."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from payment_service.application.messagebus import MessageBus
from payment_service.application.uow import UnitOfWork
from payment_service.config import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]


async def verify_api_key(
    settings: SettingsDep,
    x_api_key: Annotated[str, Header()] = '',
) -> None:
    """Проверить статический API-ключ."""
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный или отсутствующий API-ключ',
        )


def get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    """Фабрика сессий из состояния приложения."""
    factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    return factory


SessionFactoryDep = Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)]


def get_bus(session_factory: SessionFactoryDep) -> MessageBus:
    """Шина сообщений на свежем UnitOfWork."""
    return MessageBus(UnitOfWork(session_factory))


BusDep = Annotated[MessageBus, Depends(get_bus)]
