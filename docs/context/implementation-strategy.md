# Implementation Strategy

## Purpose

This document is the stable architectural and delivery reference for the platform build. It explains:

- the intended system shape
- the implementation priorities
- the main constraints and tradeoffs
- corrections to the PRD where needed

This file should change infrequently compared to the execution tracker.

## Delivery Positioning

This project should demonstrate enterprise-style continuous authentication workflows without pretending to be a production-scale rollout.

The correct target is:

- greenfield platform build
- Docker Compose-first delivery
- deployment-aware structure
- modest runtime complexity
- strong architectural clarity

## High-Level Architecture

The platform should be built from scratch as a compact modular monorepo with a small number of deployable services.

### Runtime Components

1. `backend`
   - FastAPI application
   - handles ingestion APIs, admin APIs, dashboard APIs, validation, anonymization orchestration, and policy evaluation

2. `worker`
   - processes queued jobs
   - computes historical features
   - runs model scoring
   - executes enforcement and outbound alert jobs

3. `dashboard`
   - React + Vite frontend
   - provides SOC and admin views

4. `platform services`
   - PostgreSQL
   - Redis
   - local or abstracted model artifact storage

### Deployment Model

Primary delivery format:

- Docker Compose
- environment-variable-based configuration
- clean service boundaries that can later be deployed elsewhere if needed

This project should not depend on cloud-only infrastructure to demonstrate its core value.

## Repository Structure

The agreed top-level structure is:

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

See [repo-structure.md](./repo-structure.md) for the rationale behind this layout.

## Application Layout Strategy

The application scaffolds should stay simple and framework-native.

### API

Use a layered FastAPI structure:

- `main.py` as entrypoint
- `core/` for cross-cutting runtime concerns
- `dependencies/` for FastAPI dependency providers
- `routes/` for HTTP entrypoints
- `services/` for application orchestration

Do not split `routes` and `controllers` separately for this project.

Auth should follow the same layered structure:

- auth routes in `routes/`
- auth implementation in `services/auth`

### Worker

Use a similarly simple layered structure:

- `main.py` as entrypoint
- `core/` for config, errors, and logging
- `jobs/` for job handlers
- `services/` for orchestration used by jobs

Do not introduce telemetry or worker-specific DTO packages in the initial scaffold.

### Dashboard

Keep the dashboard top-level structure close to the default Vite application layout.

Use light organization under `src/`:

- `assets`
- `components`
- `pages`
- `layouts`
- `routes`
- `services`
- `hooks`
- `lib`
- `styles`

Keep dashboard-specific formatting configuration inside `apps/dashboard`, including Prettier configuration.

## Persistence Strategy

Persistence should be shared, but migration ownership should remain repository-level rather than application-level.

Recommended split:

- `shared/domain`: business entities and rules
- `shared/database`: ORM models, repositories, session helpers, and shared persistence utilities
- `infra/migrations`: Alembic configuration and migration scripts

This allows both `api` and `worker` to use the same persistence layer without forcing database ownership into a single app or into the pure domain layer.

## Canonical Workflow

1. Tenant admin receives ingestion credentials.
2. Enterprise source sends authentication events.
3. Backend validates tenant, credential, and event-source access.
4. Backend publishes the accepted raw payload to Redis Streams.
5. Worker consumes the accepted payload through a consumer group.
6. Worker normalizes the raw payload into the canonical auth-event shape.
7. Worker anonymizes sensitive identifiers in memory and persists the canonical event in PostgreSQL.
8. Worker enforces idempotent persistence at the canonical auth-event boundary.
9. Worker publishes scoring jobs only for newly inserted auth events.
10. Worker computes user-level and global/system features from stored history.
11. Worker runs the scoring pipeline.
12. Policy layer classifies the event into safe, caution, or lockout bands.
13. Depending on operating mode, the system either logs only, alerts only, or enforces an action.
14. Dashboard surfaces scores, explanations, and operational history.

## Data and Model Strategy

### Core model assumptions

The scoring logic follows the research paper:

- AutoEncoder for global/system anomalies
- Isolation Forest for user-specific anomalies
- weighted score fusion

The platform must therefore support:

- persisted event history
- live data preparation for scoring
- model versioning
- threshold profiles

For the phase 6 MVP runtime:

- score one auth event at a time from persisted history
- use a bounded historical window for online feature preparation
- approximate `degree_centrality` from the bounded user-host graph in that window
- persist feature snapshots and host-interaction snapshots for auditability
- load trained artifacts from an explicit `artifact_metadata.json` contract rather than inferring runtime metadata from directory names

### Training pipeline

The notebook is not enough as long-term source.

The training workflow should be moved into script-based code under `training/`, while notebooks remain exploratory references.

### Serving approach

Default serving approach:

- PyTorch for the AutoEncoder
- scikit-learn for Isolation Forest

ONNX Runtime is not the default recommendation at this stage because it adds export and parity-validation complexity without clear project-scale benefit.

## Schema Strategy

Python services should share `shared/domain` and `shared/schemas` directly.

Persistence code should be shared through `shared/database`.
Redis Streams broker access should be shared through `shared/event_broker`.

For the dashboard:

- define API contracts in FastAPI/Pydantic
- expose OpenAPI
- generate TypeScript types or client code when needed

This avoids maintaining disconnected copies of API contracts across Python and TypeScript.

## Tooling Strategy

### Python

- Python 3.13
- `uv` for dependency and workspace management
- `ruff` for formatting and linting
- `mypy` for type checking

### Frontend

- React + Vite
- ESLint for linting
- Prettier for formatting

### Repository-wide

- `pre-commit` for cross-language hooks

## Scope-Conscious Build Principles

### Prefer workflow depth over infrastructure breadth

Focus on:

- one strong end-to-end pipeline
- one or two representative integrations
- one solid dashboard experience

Do not optimize for:

- many connectors
- many services
- many deployment targets

### Keep runtime simple, keep code modular

The runtime should stay small, but the code should still preserve clear boundaries between:

- ingestion
- feature computation
- scoring
- policy
- integrations

### Build local-first, not fake-cloud-first

This project should be fully demonstrable locally via Docker Compose. Cloud-readiness should come from clean boundaries and configuration, not from adding platform complexity early.

## Non-Functional Expectations

### Security

- tenant isolation
- least-privilege configuration
- auditable admin and enforcement actions

### Reliability

- idempotent ingestion
- retryable worker jobs
- dead-letter handling for failures

### Performance

- near-real-time event handling for demo workloads
- indexed feature queries on tenant, user hash, and time

### Observability

- structured logs
- correlation IDs across ingestion, scoring, and enforcement
- basic metrics around queue lag, scoring latency, and action success if they are added later without complicating the scaffold

## PRD Corrections

### `BackgroundTasks` should not be the main async engine

Use a simple queue + worker model instead of relying on FastAPI `BackgroundTasks` for core event processing.

### PostgreSQL is the system of record, not the whole workflow engine

Persist everything important in PostgreSQL, but use Redis or another lightweight broker for transient asynchronous work dispatch.

### Redis Streams is the preferred ingestion handoff

Use Redis Streams as the asynchronous handoff between the API ingestion boundary and the worker.

Recommended interpretation:

- validate ingress requests in the API
- publish accepted payloads to Redis Streams
- consume through worker-side consumer groups
- normalize and anonymize in the worker before persistence
- persist the canonical normalized event in PostgreSQL after worker processing
- enforce idempotency on `(tenant_id, idempotency_key)` during canonical event persistence
- publish downstream scoring work only for newly inserted auth events

### The ingestion worker owns normalization and canonical event persistence

The worker is the boundary that turns accepted ingress payloads into durable auth
events.

Recommended interpretation:

- keep API ingestion focused on authentication, authorization, and stream publish
- keep normalization logic in the worker ingestion services
- keep anonymization in a dedicated worker service invoked by the ingestion
  consumer
- persist only the canonical redacted auth event in PostgreSQL during this stage
- derive idempotency from canonical event content instead of raw stream delivery
- enqueue scoring as a separate downstream stream publish after successful
  canonical event persistence
- treat Redis Streams as the transient handoff, not a system of record

### "Zero-touch" ingestion still requires a canonical schema

External payloads must be adapted into one internal normalized event format.

### Anonymization must be exact, not implied

Document:

- which fields are hashed
- which are redacted
- how tenant salts are managed
- how salt changes affect historical continuity

### Thresholds must be validated in the implemented pipeline

Paper thresholds are research anchors, not guaranteed operational constants in the final implementation.

## Recommended MVP

The strongest MVP for this project is:

- multi-tenant ingestion
- PostgreSQL-backed historical feature computation
- reusable scoring service/package
- dashboard threat feed and explanation panel
- shadow mode and alert-only mode
- one real or mocked enforcement path

## Immediate Strategic Priorities

1. lock the repo conventions and agent guidance
2. scaffold the agreed top-level structure
3. set up the Python `uv` workspace and repo tooling
4. move training logic toward scripts
5. implement the ingestion-to-score path before broader integrations
