# Execution Plan

## Purpose

This is the ordered implementation tracker for the project. Unlike the other context files, this document is expected to change frequently as work progresses.

## Status Legend

- `todo`
- `in_progress`
- `done`
- `blocked`

## Phase 0: Context and Planning

- [done] Create context summaries for project scope, research assumptions, PRD interpretation, and repo structure.
- [done] Preserve source PDFs under `docs/reference`.
- [done] Create `AGENTS.md` at the repository root.

## Phase 1: Repository Scaffolding and Tooling

- [done] Scaffold the agreed top-level repository structure.
- [done] Set up Python 3.13 `uv` workspace for `apps/api`, `apps/worker`, and shared Python packages.
- [done] Add root `pyproject.toml` workspace configuration.
- [done] Set up `pre-commit` across Python and dashboard code.
- [done] Configure `ruff` for formatting and linting.
- [done] Configure `mypy` for Python type checking.
- [done] Configure dashboard `ESLint`.
- [done] Configure dashboard `Prettier`.
- [done] Add basic CI workflow under `.github`.

## Phase 2: Training Pipeline Cleanup

- [done] Create `training/` structure with `src`, `configs`, `artifacts`, and `notebooks`.
- [done] Move `model_training.ipynb` under `training/notebooks`.
- [done] Convert notebook logic into script-based training code under `training/src`.
- [done] Define reproducible training entrypoints.
- [done] Document how model artifacts are produced and versioned.

## Phase 3: Backend and Shared Foundations

- [done] Scaffold `apps/api`.
- [done] Scaffold `apps/worker`.
- [done] Scaffold `apps/dashboard` using the default Vite-style top-level structure.
- [done] Add dashboard `src` folders: `assets`, `components`, `pages`, `layouts`, `routes`, `services`, `hooks`, `lib`, `styles`.
- [done] Add Prettier configuration inside `apps/dashboard`.
- [done] Use `main.py` as the entrypoint for both `api` and `worker`.
- [done] Keep the API layout layered with `core`, `dependencies`, `routes`, and `services`.
- [done] Keep auth routes in `api/routes` and auth logic in `api/services/auth`.
- [done] Keep the worker layout minimal with `core`, `jobs`, and `services`.
- [done] Scaffold `shared/domain`.
- [done] Scaffold `shared/schemas`.
- [done] Scaffold `shared/database`.
- [done] Scaffold `shared/ml`.
- [done] Scaffold `shared/integrations`.
- [done] Scaffold `shared/policy`.
- [done] Define shared domain-driven Pydantic schemas, including the canonical authentication event schema.
- [done] Define base domain models for tenants, scores, decisions, and actions.
- [done] Implement shared database ORM models from the approved schema draft.
- [done] Configure shared async database engine, session factory, session manager, and database settings.
- [done] Add shared cache package with Redis settings, manager, and interfaces.
- [done] Wire API core runtime concerns: settings composition, logging, middleware, exception handling, infrastructure manager, and lifespan.
- [done] Wire API dependency providers for infrastructure, database, sessions, and cache access.

## Phase 4: Infrastructure Foundations

- [done] Scaffold `infra/docker`.
- [done] Scaffold `infra/migrations`.
- [done] Scaffold `infra/seed`.
- [done] Set up Alembic under `infra/migrations` with imports from `shared/database`.
- [done] Create Docker Compose setup for backend, worker, dashboard, PostgreSQL, and Redis.
- [done] Define environment variable strategy for local development.
- [done] Create initial PostgreSQL schema draft.
- [done] Create initial PostgreSQL schema and migrations.

## Phase 5: Ingestion Pipeline

- [done] Implement tenant onboarding basics.
- [done] Implement ingestion credential handling.
- [done] Implement tenant management, tenant configuration lifecycle, and event source workflows for the initial administration slice.
- [done] Add shared event broker package for Redis Streams-based ingestion dispatch.
- [done] Implement event ingestion endpoint.
- [done] Implement normalization pipeline.
- [done] Implement in-memory anonymization rules.
- [done] Persist normalized events.
- [todo] Queue scoring jobs.
- [todo] Add idempotency handling for repeated event delivery.

## Phase 6: Data Preparation and Scoring

- [todo] Implement historical event queries for model input preparation.
- [todo] Implement global/system data preparation for scoring.
- [todo] Decide MVP approach for `degree_centrality`.
- [todo] Implement scorer package based on paper architecture.
- [todo] Load model artifacts and scalers from the new pipeline layout.
- [todo] Return component scores and fused score.
- [todo] Add threshold profile support.
- [todo] Persist scores and feature snapshots.

## Phase 7: Policy and Response

- [todo] Implement policy bands: safe, caution, lockout.
- [todo] Implement operating modes: `shadow`, `alert_only`, `enforce`.
- [todo] Persist policy decisions.
- [todo] Implement outbound alert workflow.
- [todo] Implement one representative enforcement path.
- [todo] Record enforcement action history.

## Phase 8: Dashboard

- [todo] Scaffold dashboard routes and application shell.
- [todo] Integrate dashboard with backend APIs.
- [todo] Build threat feed view.
- [todo] Build event detail view.
- [todo] Build explanation panel.
- [todo] Build threshold/profile management UI.
- [todo] Build enforcement history view.
- [todo] Generate TypeScript API types or client from OpenAPI.

## Phase 9: Validation and Packaging

- [todo] Add backend tests.
- [todo] Add worker/scoring tests.
- [todo] Add dashboard tests as appropriate.
- [todo] Add end-to-end smoke flow for Docker Compose setup.
- [todo] Add demo seed data and replay scenarios.
- [todo] Add runbook and operator notes.
- [todo] Validate shadow-mode workflow.
- [todo] Validate alert-only or enforce workflow.
