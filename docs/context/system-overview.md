# Continuous Auth: System Overview

## Purpose

Continuous Auth is an enterprise-style continuous authentication platform
implemented as an applied machine-learning engineering project. It evaluates
authentication activity against historical behavioral patterns, records the
evidence used for each decision, and presents the result to an analyst.

The implementation is deployment-neutral. Docker Compose provides a reproducible
reference environment, and the same containerized services can be deployed in
cloud infrastructure. Its primary value is the complete workflow around the
UEBA model: ingestion, privacy-preserving normalization, historical feature
preparation, scoring, policy evaluation, analyst review, and controlled
response.

## Implemented capabilities

- Tenant onboarding and tenant-scoped configuration
- Provider-agnostic authentication-event ingestion
- Canonical event normalization and in-memory anonymization
- PostgreSQL persistence for events, processing evidence, scores, decisions,
  alerts, and response history
- Redis Streams handoff between the API and worker
- Bounded-window behavioral feature computation
- Hybrid global and user-level anomaly scoring
- Safe, Caution, and Lockout risk bands
- Simulation, Notify only, and Active response operating modes
- Analyst dashboard for overview, threat feed, event evidence, policies,
  activity history, and administration
- Representative Keycloak outbound enforcement integration
- Deterministic seed data for dashboard and workflow demonstration

## Scope

The project provides a credible end-to-end platform workflow with a compact
runtime architecture. Its boundaries are:

- A broad catalogue of vendor connectors
- A hyperscale event-processing architecture
- A claim that research thresholds are production-calibrated

## Core principles

1. Detection and response are separate concerns. A risk decision can be
   recorded without carrying out an external action.
2. PostgreSQL is the system of record. Redis is used for transient asynchronous
   handoff.
3. Sensitive identifiers are anonymized before normal event persistence.
4. Every scored event keeps enough processing evidence to support review.
5. The dashboard uses plain operational language while preserving technical
   detail for investigation.
6. Architecture remains modular without introducing unnecessary service
   sprawl.

## Technology baseline

- FastAPI and Python 3.13
- React, Vite, and TypeScript
- PostgreSQL
- Redis Streams
- Docker Compose
- The uv package manager, Ruff, mypy, ESLint, Prettier, and pre-commit

## Documentation boundary

The documents in this directory describe the current implementation and its
engineering rationale. They are not a task tracker or a substitute for the
implementation itself.
