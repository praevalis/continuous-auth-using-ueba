# AGENTS

## Purpose

This file defines the working contract for agents and contributors operating in this repository.

Use this document together with:

- `docs/context/project-overview.md`
- `docs/context/research-summary.md`
- `docs/context/prd-summary.md`
- `docs/context/repo-structure.md`
- `docs/context/implementation-strategy.md`
- `docs/context/execution-plan.md`

If there is a conflict between ad hoc assumptions and the context documents, follow the context documents.

## Project Positioning

This repository is a final-year engineering project that demonstrates an enterprise-style continuous authentication platform built around an existing hybrid UEBA research model.

Important scope rules:

- build greenfield
- do not reuse `~legacy` code
- optimize for technical clarity and reproducibility
- do not overengineer for production scale
- keep the system Docker Compose-first

## Source of Truth

### Primary references

- `docs/reference/research-paper.pdf`
- `docs/reference/prd.pdf`

### Working implementation context

- everything under `docs/context`

### Legacy reference

- `~legacy` is reference-only
- do not migrate or extend it as the new platform base

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
- request handling
- auth and tenant-facing orchestration
- OpenAPI generation

Should not own:

- standalone business rules that belong in `shared/domain` or `shared/policy`
- shared persistence implementation that belongs in `shared/database`

Internal scaffold direction:

- use `main.py` as the entrypoint
- keep a layered structure with `core`, `dependencies`, `routes`, and `services`
- keep auth routes under `routes`
- keep auth implementation under `services/auth`
- do not introduce a separate controller layer

### `apps/worker`

Owns:

- async job execution
- scoring pipeline orchestration
- enforcement jobs
- outbound alert jobs

Should not own:

- duplicate business logic already shared elsewhere

Internal scaffold direction:

- use `main.py` as the entrypoint
- keep a minimal layered structure with `core`, `jobs`, and `services`
- do not add worker-specific DTO or telemetry packages unless a concrete need appears later

### `apps/dashboard`

Owns:

- React + Vite frontend
- SOC/admin UI
- API consumption
- presentation logic

Should not own:

- backend business logic
- copied handwritten API contracts when generated types can be used

Internal scaffold direction:

- keep the top-level structure aligned with standard Vite output
- keep only light organization under `src`
- keep Prettier configuration inside `apps/dashboard`

### `training`

Owns:

- script-based training and model-input preparation logic
- reproducible training entrypoints
- training configs
- model artifacts metadata

Notes:

- notebooks are exploratory
- scripts are canonical

### `shared/domain`

Owns:

- business entities
- core concepts
- domain rules independent of framework and storage tooling

Should not own:

- Alembic
- FastAPI routing
- ORM migration logic
- framework-specific wiring

### `shared/schemas`

Owns:

- Python DTOs
- internal contracts
- API payload models
- queue/job payload schemas where appropriate

### `shared/database`

Owns:

- ORM models
- repositories
- session helpers
- shared persistence utilities
- query helpers shared by `api` and `worker`

### `shared/ml`

Owns:

- model loading
- model-input preparation
- inference orchestration
- score fusion implementation
- model-serving utilities

### `shared/integrations`

Owns:

- IdP adapters
- SIEM adapters
- integration clients and payload translation

### `shared/policy`

Owns:

- risk band logic
- operating mode logic
- action decision rules

### `infra/migrations`

Owns:

- Alembic configuration
- migration scripts
- schema evolution tooling

Important:

- migrations are a repository-level infrastructure concern
- `shared/database` defines persistence models
- `infra/migrations` evolves the schema based on those models

## Schema Strategy

Python services share `shared/domain`, `shared/schemas`, and `shared/database` directly.

For the dashboard:

- define API contracts in FastAPI/Pydantic
- expose OpenAPI
- generate TypeScript types or client code from OpenAPI when useful

Do not introduce unnecessary Python-to-TypeScript schema conversion layers unless there is a clear reason.

## Tooling Standards

### Python

- Python version: `3.13`
- package manager and workspace: `uv`
- linting and formatting: `ruff`
- type checking: `mypy`

### Frontend

- framework: `React + Vite`
- linting: `ESLint`
- formatting: `Prettier`

### Repository-wide

- hooks: `pre-commit`

Do not introduce Husky unless there is a compelling repo-wide reason to change the hook strategy.

## Package Export Rules

Nested packages should use curated `__init__.py` files to expose stable public exports.

Rules:

- keep internal implementation files organized at deeper paths
- expose stable symbols through package-level `__init__.py` files
- prefer importing from package entrypoints rather than deep internal modules
- do not re-export everything blindly

Treat each `__init__.py` as part of the package's public API surface.

Preferred style:

```python
from database.interfaces import UnitOfWork
from database.session import SessionManager
from database.repositories import SomeRepository
```

Avoid deep imports from outside the package unless there is a specific internal reason.

## Architecture Rules

- prefer modular monolith boundaries over microservice sprawl
- keep runtime architecture compact
- use Docker Compose as the primary execution model
- use Redis for lightweight async work dispatch
- use PostgreSQL as the system of record
- treat paper thresholds as starting points, not immutable constants
- separate detection from enforcement
- support `shadow`, `alert_only`, and `enforce` modes

## Database Rules

- business meaning belongs in `shared/domain`
- persistence implementation belongs in `shared/database`
- schema evolution belongs in `infra/migrations`
- both `api` and `worker` may read/write through the shared persistence layer

Do not collapse these concerns into one folder.

## Documentation Rules

- keep architecture guidance in `docs/context`
- keep the execution tracker updated in `docs/context/execution-plan.md`
- keep source PDFs in `docs/reference`
- when a major structural decision changes, update the relevant context docs in the same change

## Implementation Rules

- prefer script-based training code over notebook-only logic
- avoid hidden one-off local workflows
- keep code and configuration reproducible
- do not build features solely for hypothetical production scale
- when in doubt, choose the simpler design that still demonstrates the architecture cleanly

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

- prefer asking whether the change affects architecture or only implementation detail
- do not silently move responsibilities across `shared/domain`, `shared/database`, `apps/api`, and `infra/migrations`
