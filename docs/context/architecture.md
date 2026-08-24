# Current Architecture

## Runtime topology

~~~text
External event source
        |
        v
FastAPI API -----> Redis Streams -----> Worker
    |                                  |
    |                                  +--> normalization and anonymization
    |                                  +--> PostgreSQL event persistence
    |                                  +--> feature preparation and scoring
    |                                  +--> policy, alert, and response jobs
    |                                  |
    +----------------------------------+
                       |
                       v
                  PostgreSQL
                       ^
                       |
                 React dashboard
~~~

The API, worker, and dashboard are separate application processes, while the
codebase remains a modular monolith. PostgreSQL is accessed through the shared
database package, and Redis provides the lightweight asynchronous boundary.

## Ownership boundaries

| Area | Responsibility |
| --- | --- |
| apps/api | FastAPI entry points, request validation, tenant-facing orchestration, and OpenAPI |
| apps/worker | Stream consumers, scoring jobs, alert jobs, and enforcement jobs |
| apps/dashboard | React presentation, API consumption, and analyst and administration workflows |
| training | Script-based model input preparation, training configuration, and artifacts |
| shared/domain | Domain concepts, enums, and framework-independent rules |
| shared/schemas | Python API, job, and persistence-facing contracts |
| shared/database | SQLAlchemy models, repositories, sessions, and read queries |
| shared/ml | Feature preparation, model loading, inference, and score fusion |
| shared/policy | Risk bands, operating modes, and action decisions |
| shared/integrations | Provider adapters and external payload translation |
| infra/migrations | Alembic configuration and schema evolution |
| infra/seed | Reproducible API and database demonstration data |

## Event lifecycle

1. An event source submits a canonical-ingestion request with tenant-scoped
   credentials.
2. The API validates access and publishes the accepted payload to Redis
   Streams.
3. The worker normalizes vendor-shaped input into the canonical event fields.
4. Sensitive identifiers are hashed in memory and the persisted payload is
   redacted.
5. The worker stores the event idempotently in PostgreSQL.
6. A scoring job prepares a bounded historical context for the user and
   system.
7. The scoring pipeline stores feature and host-interaction snapshots,
   component scores, and the fused risk score.
8. The policy layer records a decision according to the tenant thresholds and
   operating mode.
9. Alert and response jobs record analyst-visible activity. In Active Response
   mode, a configured integration may also execute the selected provider action.

## Persistence model

Authentication events are the root of the scoring evidence chain:

~~~text
auth event
  -> processing run
  -> feature snapshot
  -> host-interaction snapshot
  -> risk score
  -> policy decision
      -> alert
      -> enforcement action
~~~

The database layer owns persistence mechanics. Domain meaning remains in the
shared domain and policy packages, while migrations remain under infra so that
schema evolution remains separate from application code.

## Operating modes

- Simulation (shadow): decisions and possible responses are recorded, but
  provider actions are not carried out.
- Notify only (alert_only): a decision produces an alert without an enforcement
  action.
- Active response (enforce): supported provider actions may be dispatched after
  policy evaluation.

The mode is a tenant setting and is evaluated independently from the risk band.
This keeps detection observable even when enforcement is disabled.

## Deployment model

Docker Compose is the reference packaging for the API, worker, dashboard,
PostgreSQL, and Redis services. Each application is containerized and
configured through environment variables, so the same service boundaries can
be deployed locally or to cloud container infrastructure. PostgreSQL and
Redis may be self-managed or provided by compatible managed services.
