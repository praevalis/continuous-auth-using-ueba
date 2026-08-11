# Repository Structure

## Purpose

This document records the intended top-level repository layout before scaffolding begins.

## Agreed Top-Level Structure

```text
/apps
  /api
  /worker
  /dashboard
/training
  /src
  /configs
  /artifacts
  /notebooks
/shared
  /domain
  /schemas
  /database
  /event_broker
  /ml
  /integrations
  /policy
/infra
  /docker
  /migrations
  /seed
/docs
  /context
  /reference
/.github
AGENTS.md
.pre-commit-config.yaml
pyproject.toml
uv.lock
```

## Rationale

### `apps`

This directory contains runnable applications:

- `api`: FastAPI backend
- `worker`: async processing service
- `dashboard`: React + Vite frontend

These are the components expected to map most directly to Docker Compose services.

Recommended internal scaffold shape:

```text
/apps
 /api
    /src
      /api
        __init__.py
        main.py
        /core
          /config
          /errors
          /logging
          /middleware
        /dependencies
        /routes
        /services
    /tests
    pyproject.toml
  /dashboard
    /public
    /src
      /components
      /hooks
      /utils
      /styles
      /api
      /features
        /overview
        /threat-feed
        /policies
        /activity
      /assets
      main.jsx|tsx
      App.jsx|tsx
    index.html
    package.json
    vite.config.js|ts
    eslint.config.js|ts
    .prettierrc
    /worker
    /src
      /worker
        __init__.py
        main.py
        /core
          /config
          /errors
          /logging
        /jobs
        /services
    /tests
    pyproject.toml
```

Notes:

- use `main.py` as the entrypoint for both `api` and `worker`
- avoid telemetry packages in the initial scaffold
- avoid worker-specific `dto` packages unless a concrete need appears later
- keep auth routes under `api/routes`
- keep auth implementation logic under `api/services/auth`
- keep the dashboard top-level structure aligned with standard Vite output
- keep dashboard formatting config local to `apps/dashboard`, including `.prettierrc`

### `training`

This directory contains the reproducible model training pipeline.

Reason for separating it from `apps`:

- training is an offline workflow, not a deployed runtime app
- notebook logic should be converted into script-based source
- future retraining should be possible without depending on notebook-only code

Suggested meaning of subdirectories:

- `src`: training and preprocessing code
- `configs`: experiment or pipeline configuration
- `artifacts`: generated outputs or tracked references
- `notebooks`: exploratory notebooks, not canonical runtime source

### `shared`

This directory contains reusable Python-side code shared across `api`, `worker`, and training where appropriate.

Suggested responsibilities:

- `domain`: core concepts and internal entities
- `schemas`: Python request, response, and internal payload models
- `database`: ORM models, repositories, session helpers, and persistence utilities shared by `api` and `worker`
- `event_broker`: shared Redis Streams settings, clients, and broker utilities used for async event dispatch
- `ml`: model loading, data preparation for inference, and scoring orchestration
- `integrations`: external system adapters
- `policy`: decision logic separated from inference logic

Worker-specific orchestration should stay under `apps/worker/services` rather than
moving into `shared` prematurely. The current ingestion worker flow is:

- `jobs/`: long-running consumer loop and batch acknowledgement flow
- `services/ingestion/normalization.py`: raw payload to canonical auth-event field derivation
- `services/ingestion/anonymization.py`: hashing and payload redaction
- `services/ingestion/persistence.py`: persistence orchestration against shared repositories
- `services/ingestion/consumer.py`: pipeline coordination from stream message to persistence payload
- `services/ingestion/score_dispatch.py`: downstream scoring-job publish after idempotent auth-event persistence

### `infra`

This directory contains environment and infrastructure support files for local reproducibility:

- Docker Compose and related config
- Alembic configuration and migration scripts under `infra/migrations`
- seed data and demo setup

### `docs`

This directory contains both source references and working context:

- `reference`: original PDFs and other primary reference material
- `context`: implementation-facing summaries and decisions

## Database Ownership Strategy

The database is not owned by `domain` alone.

Recommended split:

- `shared/domain`: business concepts and rules
- `shared/database`: persistence implementation
- `infra/migrations`: schema evolution

This keeps business meaning separate from ORM, repositories, and migration tooling while still allowing both `api` and `worker` to share the same persistence layer.

## Schema Strategy

Python services can share `shared/domain` and `shared/schemas` directly.

The dashboard should not maintain independent handwritten copies of backend contracts where avoidable. The preferred approach is:

- define API contracts in FastAPI/Pydantic
- expose OpenAPI
- generate TypeScript types or client code for the dashboard as needed

## Package Management Strategy

Python 3.13 and `uv` are the chosen tooling baseline.

Recommended interpretation:

- use a `uv` workspace for Python applications and shared Python packages
- keep the dashboard in the Node ecosystem with its own `package.json`
- keep repository-wide hooks and standards at the root

## Tooling Strategy

- Python formatting and linting: `ruff`
- Python type checking: `mypy`
- frontend formatting: `Prettier`
- frontend linting: `ESLint`
- repository-wide git hooks: `pre-commit`

## Package Export Strategy

Nested packages should use curated `__init__.py` files to expose stable public exports.

Goal:

- keep internal implementation files organized
- keep imports used by `api`, `worker`, and other packages simple
- reduce deep import-path coupling

Recommended practice:

- re-export only stable public symbols
- treat package-level `__init__.py` files as the public API surface for that package
- avoid importing from deep internal modules unless working inside that package itself

Example intent:

```python
from database.interfaces import UnitOfWork
from database.session import SessionManager
from database.repositories import SomeRepository
```

Prefer this over deep imports into internal module files from outside the package.

## Deliberate Constraints

This structure is modular, but intentionally not microservice-heavy. The goal is:

- clean boundaries
- low operational overhead
- strong explainability during implementation and review
