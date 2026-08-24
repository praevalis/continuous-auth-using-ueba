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
docker compose up -d
~~~

Apply the database migrations with the repository Alembic configuration:

~~~bash
uv run alembic -c infra/migrations/alembic.ini upgrade head
~~~

## Deterministic seed

The seed workflow has two stages:

1. infra/seed/seed_api.py exercises the API path by creating or reusing tenant
   resources and submitting a replay event.
2. infra/seed/seed_database.py loads the related dashboard records through the
   shared persistence models.

Run the API seed first and the database seed second. The complete procedure,
options, and environment notes are documented in infra/seed/README.md.

The seed data intentionally covers safe, caution, lockout, unscored, simulated,
pending, failed, acknowledged, and resolved states so the dashboard can be
reviewed without waiting for naturally occurring events.

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
- The reference stack is the baseline for demonstration and review.

This document describes repeatable operation of the current repository and the
deployment assumptions that make the runtime portable across environments.
