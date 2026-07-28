# PRD Summary

## Source

- [prd.pdf](../reference/prd.pdf)

## PRD Intent

The PRD asks for a continuous authentication platform built around the research model, with enterprise-style ingestion, scoring, analyst visibility, and response workflows.

## Requirements Extracted From the PRD

### Tenant and onboarding

- support enterprise or tenant registration
- store tenant-specific settings
- issue ingestion credentials

### Event ingestion

- accept authentication-related events from enterprise systems
- support standard input formats such as JSON or Syslog-like payloads
- normalize vendor-specific payloads into a canonical event shape

### Privacy and anonymization

- hash sensitive identifiers in memory before persistence
- avoid storing raw user identifiers in normal event-processing paths

### Storage

- persist enterprise metadata
- persist normalized events
- persist model outputs and related operational data

### Feature computation and scoring

- compute historical temporal behavior features from stored data
- compute global/system features required by the model
- run the hybrid scoring pipeline
- store scores for later review

### Modes of operation

- support shadow mode
- support active decision thresholds
- separate detection from enforcement

### Enforcement

- support MFA-like caution responses
- support session termination or lockout on high-risk behavior
- integrate with at least representative IdP flows

### Analyst workflow

- show live or near-live threat feed
- visualize score components
- support an explanation view
- allow threshold or calibration controls

### Packaging

- provide an easy evaluator setup
- support containerized execution

## Corrections and Clarifications

### `BackgroundTasks` should not be the core workflow engine

The PRD mentions FastAPI `BackgroundTasks`. That is acceptable for minor background work, but not as the main durable event-processing approach.

Preferred interpretation:

- use a simple queue + worker model
- keep runtime compact
- do not overbuild orchestration

### PostgreSQL is the system of record, not the whole async architecture

The PRD correctly centers PostgreSQL, but event dispatch should still use a lightweight queue to avoid coupling ingestion and scoring too tightly.

### "Zero-touch" ingestion needs a canonical contract

Different event sources will differ. The practical implementation should define one internal event schema and adapt inputs into that schema.

### Anonymization needs versioned rules

The PRD calls for tenant-specific hashing. The implementation should document:

- which fields are hashed
- how salts are managed
- how future salt rotation would affect baseline continuity

### Thresholds need platform validation

The PRD references the model operationally, but threshold behavior depends on preprocessing parity. Paper thresholds should be treated as validated starting assumptions, not immutable constants.

## Student-Project Interpretation

The correct scope is:

- simulate enterprise workflows faithfully
- implement a compact but realistic runtime
- use Docker Compose instead of full deployment infrastructure
- prefer one or two strong integrations over broad connector coverage

## Implementation Priorities

1. ingestion and normalization
2. persistent history and feature computation
3. model scoring package
4. policy and shadow mode
5. dashboard and explanation flow
6. one strong IdP or SIEM integration path
