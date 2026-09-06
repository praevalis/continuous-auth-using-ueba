# Reproducibility and Deployment

## Reference environment

Docker Compose provides the reproducible reference environment. It runs:

- API at http://localhost:8000
- Dashboard at http://localhost:5173
- PostgreSQL on host port 5434
- Redis on host port 6380

The application containers communicate over the Compose network. Environment
variables provide database, Redis, and API configuration.

## Deployment portability

The API, worker, and dashboard are independently containerized. Their runtime
configuration is supplied through environment variables rather than hard-coded
local dependencies. The same services can therefore be deployed with Docker
Compose for evaluation or with a cloud container platform, using self-managed
or managed PostgreSQL and Redis services.

## Setup

Install the Python workspace:

~~~bash
uv sync
~~~

Start the services:

~~~bash
docker compose up -d --build
~~~

Compose waits for PostgreSQL, applies every Alembic migration through the
one-shot `migrate` service, starts the API and worker only after migration
success, and runs the one-shot `platform-seed` service after the API becomes
healthy. A migration failure prevents dependent application services from
starting, and a seed failure remains visible as a failed one-shot container.

## Deterministic seed

The seed workflow has two stages orchestrated by
`infra/seed/seed_platform.py` inside Docker Compose:

1. infra/seed/seed_api.py exercises the API path by creating or reusing tenant
   resources and submitting a replay event.
2. infra/seed/seed_database.py loads the related dashboard records through the
   shared persistence models.

For manual execution, run the API seed first and the database seed second. The
complete automatic and manual procedures, options, and environment notes are
documented in infra/seed/README.md.

The database seed contains 20 scored examples selected from the `baseline-v4`
held-out evaluation window, preserving their version-2 feature values and model
scores. Their timestamps are shifted by whole weeks to remain inside the
reference environment's 30-day dashboard filters without changing weekday
features. The fixture is intentionally stratified as 75% safe, 20% caution, and
5% lockout for dashboard coverage rather than as a claim about the natural
production distribution. Together with the API replay event, it covers safe,
caution, lockout, simulated, pending, failed, acknowledged, and resolved states
without waiting for naturally occurring events. The replay event uses its
submission time and passes through the live worker pipeline, so its eventual
score is outside the fixed fixture distribution.

## Quality checks

~~~bash
pre-commit run --all-files
uv run ruff check .
npm --prefix apps/dashboard run lint
npm --prefix apps/dashboard run typecheck
npm --prefix apps/dashboard run build
~~~

## Reproducibility notes

- Python dependencies are locked through uv.lock.
- Database evolution is represented by Alembic migrations.
- API contracts are generated from the FastAPI OpenAPI surface.
- Seed identifiers are deterministic for repeatable database loading.
- Model artifacts and their metadata are kept under training/artifacts.
- The worker defaults to the promoted `baseline-v4` artifact bundle; deployments
  may override the run directory through `SCORING_MODEL_RUN_DIRECTORY`.
- Training data selection, temporal evaluation, and the artifact contract are
  documented in [training.md](./training.md).
- The reference stack is the baseline for demonstration and review.

This document describes repeatable operation of the current repository and the
deployment assumptions that make the runtime portable across environments.
