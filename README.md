# Continuous Authentication Using UEBA

Continuous Auth is a Docker Compose-first platform for continuous
authentication using a hybrid User and Entity Behavior Analytics (UEBA) model.

The repository contains end-to-end workflow from authentication-event
ingestion through historical feature preparation, hybrid anomaly scoring, risk
policy evaluation, analyst review, and optional provider enforcement.

## Architecture

The system is a compact modular monolith with separate runtime processes:

- FastAPI API for ingestion, tenant administration, dashboard reads, and
  configuration workflows
- Python worker for Redis-backed event processing, feature computation, scoring,
  alerting, and enforcement jobs
- React + Vite dashboard for analyst and tenant administration workflows
- PostgreSQL as the system of record
- Redis Streams for lightweight asynchronous handoff
- Keycloak as the representative outbound identity-provider integration

Docker Compose is the reference packaging for local development and evaluation.
The services use standard containers and environment-based configuration, so
the same runtime can be deployed to cloud container infrastructure.

## Repository layout

```text
apps/       Runnable API, worker, and dashboard applications
shared/     Domain, schema, persistence, ML, policy, and integration packages
training/   Reproducible model-input and artifact preparation
infra/      Docker, migrations, and deterministic seed data
docs/       Maintained project documentation and review material
```

Start with [docs/context/README.md](docs/context/README.md) for the project
documentation index.

## Tooling

- Python 3.13 with uv
- Ruff and mypy
- React, Vite, TypeScript, ESLint, and Prettier
- Pre-commit
- Docker Compose

## Local development

Install the Python workspace:

```bash
uv sync
```

Start the complete local stack:

```bash
docker compose up -d
```

The dashboard is available at http://localhost:5173 and the API at
http://localhost:8000.

To load the deterministic seed dataset, follow the
[seed loader instructions](infra/seed/README.md) after the services are
healthy.

## Quality checks

Run repository hooks:

```bash
pre-commit run --all-files
```

Run dashboard checks:

```bash
npm --prefix apps/dashboard run lint
npm --prefix apps/dashboard run typecheck
npm --prefix apps/dashboard run build
```

## Project status

The core platform implementation and dashboard workflows are complete. Further
work should be treated as deliberate feature development or hardening, with
architecture changes documented alongside the code.
