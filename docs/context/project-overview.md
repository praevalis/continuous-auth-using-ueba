# Project Overview

## Purpose

This project is a final-year AI and Data Science engineering project that aims to demonstrate an enterprise-style continuous authentication platform built around a hybrid UEBA model.

The research model architecture already exists. The remaining work is to build the platform workflow around it:

- event ingestion
- historical feature computation
- model scoring
- policy evaluation
- analyst visibility
- optional enforcement integrations

## What This Project Is

This is:

- a greenfield platform build
- a Docker Compose-first system
- a technically credible enterprise workflow demonstration
- a software engineering project built around an applied ML core

## What This Project Is Not

This is not:

- a production rollout
- a hyperscale distributed system
- a microservices-heavy cloud platform
- a continuation of the legacy proof-of-concept implementation

## Scope Positioning

The platform should support enterprise operations conceptually, but the implementation should stay proportional to a student project.

The expected balance is:

- realistic workflows and architecture boundaries
- modest runtime complexity
- local reproducibility
- deployment-aware design without overengineering

## Primary Goals

- package the research model into a reusable scoring component
- ingest authentication events in near real time
- compute live behavioral features from persisted event history
- produce anomaly scores and risk decisions
- support analyst review through a dashboard
- demonstrate shadow mode and controlled response workflows

## Non-Goals

- multi-region deployments
- high-availability clustering
- wide connector coverage across many vendors
- production-grade scale optimizations without measured need

## Reference Documents

- [research-paper.pdf](../reference/research-paper.pdf)
- [prd.pdf](../reference/prd.pdf)

## Current High-Level Stack Direction

- frontend: React + Vite
- backend: FastAPI
- worker: Python async worker
- database: PostgreSQL
- queue: Redis
- packaging: Docker Compose
- Python tooling: Python 3.13 + `uv`

## Important Working Assumptions

- `~legacy` is reference only and will not be reused
- the research paper is the source of truth for the model logic
- the PRD is the source of truth for platform direction, but not all wording should be implemented literally
- implementation decisions should favor clarity and reproducibility over premature scale
