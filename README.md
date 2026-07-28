# Continuous Authentication Using UEBA

## Overview

This repository contains an enterprise-style continuous authentication platform around a hybrid UEBA research model.

The platform is being built with:

- FastAPI backend
- Python worker
- React + Vite dashboard
- PostgreSQL
- Redis
- Docker Compose

## Repository Structure

```text
apps/
  api/
  worker/
  dashboard/
training/
shared/
infra/
docs/
```

Key references:

- `docs/context/`
- `docs/reference/`
- `AGENTS.md`

## Tooling

- Python `3.13`
- `uv` workspace
- `ruff`
- `mypy`
- `pre-commit`
- `ESLint`
- `Prettier`

## Local Setup

### Python workspace

```bash
uv sync
```

### Dashboard

```bash
npm --prefix apps/dashboard install
```

### Infrastructure

```bash
docker compose up -d
```

This currently starts:

- PostgreSQL
- Redis

## Quality Checks

Run repository hooks:

```bash
pre-commit run --all-files
```

Run dashboard linting:

```bash
npm --prefix apps/dashboard run lint
```

Run dashboard formatting:

```bash
npm --prefix apps/dashboard run format
```

## Status

The repository is currently scaffolded and ready for implementation work. The next phase is building the actual platform logic on top of the established structure.
