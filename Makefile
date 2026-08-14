.PHONY: install lint format typecheck migrate run-api run-consumer up down check

install:
	uv sync

lint:
	uv run ruff check src alembic
	uv run ruff format --check src alembic

format:
	uv run ruff format src alembic

typecheck:
	uv run mypy src

migrate:
	uv run alembic upgrade head

run-api:
	uv run uvicorn payment_service.api.main:app --reload

run-consumer:
	uv run python -m payment_service.consumer.main

up:
	docker compose up -d --build

down:
	docker compose down

check: lint format typecheck
