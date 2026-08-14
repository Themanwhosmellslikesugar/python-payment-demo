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

## API

Все эндпоинты требуют заголовок `X-API-Key` (по умолчанию `dev-api-key`).

Создание платежа (обязателен заголовок `Idempotency-Key`):

```bash
curl -X POST http://localhost:8080/api/v1/payments \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: dev-api-key' \
  -H 'Idempotency-Key: order-42' \
  -d '{
    "amount": "100.50",
    "currency": "RUB",
    "description": "Оплата заказа",
    "metadata": {"order_id": 42},
    "webhook_url": "http://example.com/hook"
  }'
```

Ответ `202 Accepted`:

```json
{"payment_id": "...", "status": "pending", "created_at": "..."}
```

Повторный запрос с тем же `Idempotency-Key` вернёт тот же платёж.

Получение платежа:

```bash
curl http://localhost:8080/api/v1/payments/{payment_id} -H 'X-API-Key: dev-api-key'
```
