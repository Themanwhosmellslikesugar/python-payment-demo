FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim@sha256:dded2f5cb3c42d70de1a852167a0c3aa9f7d74e67d348193ae49d37fd72f54c7

RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

WORKDIR /app

ENV PYTHONUNBUFFERED=1

ENV UV_COMPILE_BYTECODE=1

ENV UV_LINK_MODE=copy

ENV UV_NO_DEV=1

ENV UV_TOOL_BIN_DIR=/usr/local/bin

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT []

USER nonroot

CMD ["uvicorn", "payment_service.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
