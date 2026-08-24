# AGENTS

## Purpose

This file defines the working contract for agents and contributors operating in this repository.

Use this document together with the maintained project context:

- `docs/context/README.md`
- `docs/context/system-overview.md`
- `docs/context/architecture.md`
- `docs/context/model-and-policy.md`
- `docs/context/dashboard.md`
- `docs/context/reproducibility.md`

If there is a conflict between ad hoc assumptions and the context documents, follow the context documents.

## Project Positioning

This repository contains an enterprise-style continuous authentication platform built around a hybrid UEBA research model.

Important scope rules:

- Preserve the implemented ownership boundaries
- Preserve technical clarity and reproducibility
- Keep architecture modular and deployment-neutral
- Use Docker Compose as the reference packaging

## Source of Truth

### Maintained project context

- `docs/context` contains the current system documentation.
- The code, tests, migrations, and seed workflow are the implementation sources of truth.

### Documentation boundary

- Implementation guidance belongs in the maintained documents listed above
- Completed work should be verified against the code, tests, migrations, and seed workflow

## Repository Structure

Expected top-level layout:

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

## Ownership Boundaries

### `apps/api`

Owns:

- FastAPI entrypoints
- API routing
- Request handling
- Auth and tenant-facing orchestration
- OpenAPI generation

Should not own:

- Standalone business rules that belong in `shared/domain` or `shared/policy`
- Shared persistence implementation that belongs in `shared/database`

Internal scaffold direction:

- Use `main.py` as the entrypoint
- Keep a layered structure with `core`, `dependencies`, `routes`, and `services`
- Keep auth routes under `routes`
- Keep auth implementation under `services/auth`
- Do not introduce a separate controller layer

### `apps/worker`

Owns:

- Async job execution
- Scoring pipeline orchestration
- Enforcement jobs
- Outbound alert jobs

Should not own:

- Duplicate business logic already shared elsewhere

Internal scaffold direction:

- Use `main.py` as the entrypoint
- Keep a minimal layered structure with `core`, `jobs`, and `services`
- Do not add worker-specific DTO or telemetry packages unless a concrete need appears later

### `apps/dashboard`

Owns:

- React + Vite frontend
- SOC/admin UI
- API consumption
- Presentation logic

Should not own:

- Backend business logic
- Copied handwritten API contracts when generated types can be used

Internal scaffold direction:

- Keep the top-level structure aligned with standard Vite output
- Keep only light organization under `src`
- Keep Prettier configuration inside `apps/dashboard`

### `training`

Owns:

- Script-based training and model-input preparation logic
- Reproducible training entrypoints
- Training configs
- Model artifacts metadata

Notes:

- Notebooks are exploratory
- Scripts are canonical

### `shared/domain`

Owns:

- Business entities
- Core concepts
- Domain rules independent of framework and storage tooling

Should not own:

- Alembic
- FastAPI routing
- ORM migration logic
- Framework-specific wiring

### `shared/schemas`

Owns:

- Python DTOs
- Internal contracts
- API payload models
- Queue/job payload schemas where appropriate

### `shared/database`

Owns:

- ORM models
- Repositories
- Session helpers
- Shared persistence utilities
- Query helpers shared by `api` and `worker`

### `shared/ml`

Owns:

- Model loading
- Model-input preparation
- Inference orchestration
- Score fusion implementation
- Model-serving utilities

### `shared/integrations`

Owns:

- IdP adapters
- SIEM adapters
- Integration clients and payload translation

### `shared/policy`

Owns:

- Risk band logic
- Operating mode logic
- Action decision rules

### `infra/migrations`

Owns:

- Alembic configuration
- Migration scripts
- Schema evolution tooling

Important:

- Migrations are a repository-level infrastructure concern
- `shared/database` defines persistence models
- `infra/migrations` evolves the schema based on those models

## Schema Strategy

Python services share `shared/domain`, `shared/schemas`, and `shared/database` directly.

For the dashboard:

- Define API contracts in FastAPI/Pydantic
- Expose OpenAPI
- Generate TypeScript types or client code from OpenAPI when useful

Do not introduce unnecessary Python-to-TypeScript schema conversion layers unless there is a clear reason.

## Tooling Standards

### Python

- Python version: `3.13`
- Package manager and workspace: `uv`
- Linting and formatting: `ruff`
- Type checking: `mypy`

### Frontend

- Framework: `React + Vite`
- Linting: `ESLint`
- Formatting: `Prettier`

### Repository-wide

- Hooks: `pre-commit`

Do not introduce Husky unless there is a compelling repo-wide reason to change the hook strategy.

## Package Export Rules

Nested packages should use curated `__init__.py` files to expose stable public exports.

Rules:

- Keep internal implementation files organized at deeper paths
- Expose stable symbols through package-level `__init__.py` files
- Prefer importing from package entrypoints rather than deep internal modules
- Do not re-export everything blindly

Treat each `__init__.py` as part of the package's public API surface.

Preferred style:

```python
from database.interfaces import UnitOfWork
from database.session import SessionManager
from database.repositories import SomeRepository
```

Avoid deep imports from outside the package unless there is a specific internal reason.

## Architecture Rules

- Prefer modular monolith boundaries over microservice sprawl
- Keep runtime architecture compact
- Use Docker Compose as the reference packaging
- Use Redis for lightweight async work dispatch
- Use PostgreSQL as the system of record
- Treat configured thresholds as explicit tenant settings
- Separate detection from enforcement
- Support `shadow`, `alert_only`, and `enforce` modes

## Database Rules

- Business meaning belongs in `shared/domain`
- Persistence implementation belongs in `shared/database`
- Schema evolution belongs in `infra/migrations`
- Both `api` and `worker` may read/write through the shared persistence layer

Do not collapse these concerns into one folder.

## Documentation Rules

- Keep current architecture and workflow guidance in `docs/context`
- When a structural decision changes, update the relevant current-system document in the same change

## Implementation Rules

- Prefer script-based training code over notebook-only logic
- Avoid hidden one-off workflows
- Keep code and configuration reproducible
- Keep deployment configuration explicit and portable
- When in doubt, choose the simpler design that still demonstrates the architecture cleanly

## Agent Behavior

Before major implementation work:

1. read the relevant files in `docs/context`
2. verify where the change belongs
3. avoid creating new structural patterns unless necessary

When making structural changes:

1. update the relevant context documents
2. keep naming consistent with existing conventions
3. preserve the agreed ownership boundaries

When uncertain:

- Prefer asking whether the change affects architecture or only implementation detail
- Do not silently move responsibilities across `shared/domain`, `shared/database`, `apps/api`, and `infra/migrations`
