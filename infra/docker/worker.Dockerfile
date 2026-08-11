FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
COPY apps/api/pyproject.toml apps/api/pyproject.toml
COPY apps/worker/pyproject.toml apps/worker/pyproject.toml
COPY training/pyproject.toml training/pyproject.toml
COPY shared/domain/pyproject.toml shared/domain/pyproject.toml
COPY shared/schemas/pyproject.toml shared/schemas/pyproject.toml
COPY shared/database/pyproject.toml shared/database/pyproject.toml
COPY shared/cache/pyproject.toml shared/cache/pyproject.toml
COPY shared/event_broker/pyproject.toml shared/event_broker/pyproject.toml
COPY shared/ml/pyproject.toml shared/ml/pyproject.toml
COPY shared/integrations/pyproject.toml shared/integrations/pyproject.toml
COPY shared/policy/pyproject.toml shared/policy/pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package continuous-auth-worker --no-install-workspace

COPY apps/worker/src apps/worker/src
COPY shared/domain/src shared/domain/src
COPY shared/schemas/src shared/schemas/src
COPY shared/database/src shared/database/src
COPY shared/event_broker/src shared/event_broker/src
COPY shared/integrations/src shared/integrations/src
COPY shared/ml/src shared/ml/src
COPY shared/policy/src shared/policy/src
COPY training/artifacts training/artifacts
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package continuous-auth-worker

FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv
COPY apps/worker/src apps/worker/src
COPY shared/domain/src shared/domain/src
COPY shared/schemas/src shared/schemas/src
COPY shared/database/src shared/database/src
COPY shared/event_broker/src shared/event_broker/src
COPY shared/integrations/src shared/integrations/src
COPY shared/ml/src shared/ml/src
COPY shared/policy/src shared/policy/src
COPY training/artifacts training/artifacts

CMD ["python", "-m", "worker.main"]
