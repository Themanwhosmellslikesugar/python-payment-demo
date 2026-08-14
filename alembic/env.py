"""Конфигурация Alembic."""

from __future__ import annotations

import asyncio
from logging.config import fileConfig
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from payment_service.config import get_settings
from payment_service.infrastructure.db.base import Base
from payment_service.infrastructure.db.tables import OutboxTable, PaymentTable  # noqa: F401

if TYPE_CHECKING:
    from sqlalchemy import Connection

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Миграции в офлайн-режиме (генерация SQL)."""
    context.configure(
        url=get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Миграции на переданном соединении."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Миграции в онлайн-режиме через асинхронный движок."""
    engine = create_async_engine(get_settings().database_url)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
