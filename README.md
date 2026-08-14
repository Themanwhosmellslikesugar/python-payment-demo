# payment-service

Асинхронный сервис процессинга платежей. API принимает платёж, событие через
outbox попадает в RabbitMQ, consumer эмулирует обработку во внешнем шлюзе
(2–5 сек, 90% успех), обновляет статус и отправляет webhook-уведомление.

Стек: FastAPI + Pydantic v2, SQLAlchemy 2.0 (async, psycopg), PostgreSQL,
RabbitMQ (FastStream), Alembic, Docker.

## Запуск

```bash
make up        # docker compose up -d --build (postgres, rabbitmq, migrate, api, consumer)
make down      # остановить всё
```

API поднимется на `http://localhost:8080`, UI RabbitMQ — `http://localhost:15673`
(guest/guest).

## Команды

```bash
make install       # uv sync
make lint          # ruff check + ruff format --check
make format        # ruff format
make typecheck     # mypy (strict)
make check         # lint + format + typecheck
make migrate       # alembic upgrade head (локально, против compose-порта 5433)
make run-api       # локальный запуск API с reload
make run-consumer  # локальный запуск consumer'а
```
