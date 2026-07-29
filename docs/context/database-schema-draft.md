# Database Schema Draft

## Purpose

This document proposes the initial PostgreSQL schema for the continuous authentication platform.

It is an implementation-facing draft for review before:

- defining the canonical authentication event schema in `shared/schemas`
- finalizing domain models in `shared/domain`
- implementing ORM models in `shared/database`
- creating Alembic migrations in `infra/migrations`

This draft is intentionally conservative. It favors auditability, tenant isolation, and reproducible scoring workflows over production-scale optimization.

## Design Principles

- PostgreSQL is the system of record for tenants, normalized events, scores, decisions, and action history.
- Redis remains the transient job-dispatch mechanism; database tables capture audit and retry state, not queue semantics alone.
- Sensitive identifiers should be hashed before persistence in normal event-processing paths.
- Tenant-specific configuration should be explicit and versionable.
- Detection data and enforcement data should remain separate but linkable.
- The schema should support `shadow`, `alert_only`, and `enforce` operating modes.

## Main Entity Groups

The initial schema should cover these groups:

1. tenant and configuration data
2. ingestion and source-system identity
3. normalized authentication events
4. scoring and feature snapshots
5. policy decisions
6. enforcement and alert history

## Proposed Tables

### `tenants`

Purpose:
Represents an onboarded enterprise or demo tenant.

Suggested fields:

- `id` UUID primary key
- `slug` text unique, stable human-readable identifier
- `display_name` text
- `status` enum: `active`, `suspended`, `archived`
- `default_timezone` text
- `created_at` timestamptz
- `updated_at` timestamptz

Notes:

- `slug` should be stable enough for configuration and seeded demos.
- Do not overload this table with threshold or anonymization settings.

### `tenant_operating_modes`

Purpose:
Stores the current and historical platform operating mode per tenant.

Suggested fields:

- `id` UUID primary key
- `tenant_id` UUID foreign key to `tenants`
- `mode` enum: `shadow`, `alert_only`, `enforce`
- `is_active` boolean
- `effective_from` timestamptz
- `effective_to` timestamptz nullable
- `changed_by` text nullable
- `change_reason` text nullable
- `created_at` timestamptz

Notes:

- Keeping this separate allows mode changes to be audited over time.
- Only one row per tenant should be active at a time.

### `tenant_threshold_profiles`

Purpose:
Stores score-threshold configuration and policy tuning per tenant.

Suggested fields:

- `id` UUID primary key
- `tenant_id` UUID foreign key to `tenants`
- `name` text
- `description` text nullable
- `caution_threshold` numeric
- `lockout_threshold` numeric
- `fusion_alpha` numeric nullable
- `is_active` boolean
- `effective_from` timestamptz
- `effective_to` timestamptz nullable
- `created_at` timestamptz
- `updated_at` timestamptz

Notes:

- This supports paper defaults as starting values without hard-coding them globally.
- Only one profile per tenant should be active at a time for MVP.

### `tenant_hash_key_versions`

Purpose:
Tracks tenant-specific anonymization key versions used when hashing identifiers.

Suggested fields:

- `id` UUID primary key
- `tenant_id` UUID foreign key to `tenants`
- `key_version` integer
- `algorithm` text
- `salt_value` text
- `is_active` boolean
- `effective_from` timestamptz
- `effective_to` timestamptz nullable
- `created_at` timestamptz

Notes:

- `salt_value` stores the tenant salt directly for MVP simplicity and local reproducibility.
- This field should be treated as internal configuration and should not be exposed through API- or dashboard-facing schema surfaces.
- Persisting `key_version` on derived records preserves continuity across rotations.

### `event_sources`

Purpose:
Represents a logical source integration that sends authentication events for a tenant.

Suggested fields:

- `id` UUID primary key
- `tenant_id` UUID foreign key to `tenants`
- `source_name` text
- `source_type` enum: `idp`, `siem`, `agent`, `manual_replay`
- `vendor` text nullable
- `external_reference` text nullable
- `status` enum: `active`, `disabled`
- `created_at` timestamptz
- `updated_at` timestamptz

Notes:

- This avoids embedding vendor/source identity directly in credentials or events alone.

### `ingestion_credentials`

Purpose:
Stores tenant-issued credentials used to submit events.

Suggested fields:

- `id` UUID primary key
- `tenant_id` UUID foreign key to `tenants`
- `event_source_id` UUID foreign key to `event_sources` nullable
- `credential_name` text
- `credential_type` enum: `api_key`
- `key_id` text unique
- `key_hash` text
- `status` enum: `active`, `revoked`, `expired`
- `expires_at` timestamptz nullable
- `last_used_at` timestamptz nullable
- `created_at` timestamptz
- `rotated_at` timestamptz nullable

Notes:

- Store only a verifiable hash of the credential secret.
- `key_id` can remain non-secret and appear in logs or request metadata.

### `auth_events`

Purpose:
Stores the canonical normalized authentication event after validation and in-memory anonymization.

Suggested fields:

- `id` UUID primary key
- `tenant_id` UUID foreign key to `tenants`
- `event_source_id` UUID foreign key to `event_sources`
- `ingestion_credential_id` UUID foreign key to `ingestion_credentials` nullable
- `source_event_id` text nullable
- `idempotency_key` text
- `occurred_at` timestamptz
- `ingested_at` timestamptz
- `event_type` text
- `outcome` enum: `success`, `failure`, `challenge`, `logout`, `unknown`
- `user_hash` text
- `account_hash` text nullable
- `session_hash` text nullable
- `source_ip_hash` text nullable
- `source_ip_prefix` text nullable
- `device_hash` text nullable
- `host_hash` text nullable
- `auth_method` text nullable
- `failure_reason` text nullable
- `location_country` text nullable
- `location_region` text nullable
- `occurred_hour` smallint
- `occurred_day_of_week` smallint
- `hash_key_version` integer
- `payload_schema_version` integer
- `raw_payload_redacted` jsonb nullable
- `normalization_metadata` jsonb nullable
- `created_at` timestamptz

Notes:

- `idempotency_key` should be unique per tenant.
- `source_ip_prefix` is optional but useful if you want limited analyst filtering without retaining raw IPs.
- `occurred_hour` and `occurred_day_of_week` are denormalized because they are core model features and common filters.
- Keep the canonical shape stable even if vendor-specific fields vary.

### `event_processing_runs`

Purpose:
Captures scoring-pipeline processing attempts for audit, retry tracking, and operational visibility.

Suggested fields:

- `id` UUID primary key
- `tenant_id` UUID foreign key to `tenants`
- `auth_event_id` UUID foreign key to `auth_events`
- `job_type` enum: `score_event`, `send_alert`, `enforce_action`
- `status` enum: `queued`, `running`, `succeeded`, `failed`, `dead_lettered`
- `attempt_count` integer
- `correlation_id` text nullable
- `error_code` text nullable
- `error_message` text nullable
- `queued_at` timestamptz
- `started_at` timestamptz nullable
- `finished_at` timestamptz nullable
- `created_at` timestamptz

Notes:

- This is not a replacement for Redis.
- It gives the dashboard and operators a persisted view of processing health.

### `feature_snapshots`

Purpose:
Stores the computed feature values used for a specific scoring run.

Suggested fields:

- `id` UUID primary key
- `tenant_id` UUID foreign key to `tenants`
- `auth_event_id` UUID foreign key to `auth_events`
- `processing_run_id` UUID foreign key to `event_processing_runs`
- `window_start` timestamptz nullable
- `window_end` timestamptz nullable
- `login_frequency` numeric nullable
- `avg_inter_event_time` numeric nullable
- `time_since_last_login` numeric nullable
- `unique_hosts` numeric nullable
- `host_entropy` numeric nullable
- `top_host_ratio` numeric nullable
- `degree_centrality` numeric nullable
- `hour_of_day` smallint
- `day_of_week` smallint
- `feature_version` integer
- `computed_at` timestamptz

Notes:

- Keeping features in columns makes score debugging and paper-parity validation easier.
- If additional derived values are needed later, add a `feature_metadata` JSONB column rather than forcing premature schema breadth now.

### `host_interaction_snapshots`

Purpose:
Stores the time-bounded user-host interaction data needed to recompute graph-derived features such as `degree_centrality`.

Suggested fields:

- `id` UUID primary key
- `tenant_id` UUID foreign key to `tenants`
- `auth_event_id` UUID foreign key to `auth_events`
- `processing_run_id` UUID foreign key to `event_processing_runs`
- `window_start` timestamptz
- `window_end` timestamptz
- `user_hash` text
- `host_hash` text
- `interaction_count` integer
- `last_interaction_at` timestamptz
- `snapshot_version` integer
- `computed_at` timestamptz

Notes:

- This is the minimal persisted graph-support structure for MVP.
- It is intentionally an aggregated snapshot table, not a generic graph-edge store.
- It gives the worker enough data to rebuild a local bipartite graph for scoring windows without introducing a broader graph-model subsystem yet.
- `interaction_count` is a derived aggregate for a specific processing window, not a mutable shared counter updated by concurrent ingestion requests.
- Ingestion should remain append-only into `auth_events`; the worker should compute or recompute these snapshot rows from source-of-truth events.
- For retries or reprocessing, prefer writing a new snapshot tied to a new `processing_run_id`, or use an idempotent upsert keyed by the snapshot identity for that exact window.

### `risk_scores`

Purpose:
Stores component-level and fused anomaly scores for an event.

Suggested fields:

- `id` UUID primary key
- `tenant_id` UUID foreign key to `tenants`
- `auth_event_id` UUID foreign key to `auth_events`
- `feature_snapshot_id` UUID foreign key to `feature_snapshots`
- `processing_run_id` UUID foreign key to `event_processing_runs`
- `model_version` text
- `threshold_profile_id` UUID foreign key to `tenant_threshold_profiles`
- `global_anomaly_score` numeric
- `local_anomaly_score_raw` numeric
- `local_anomaly_score_normalized` numeric
- `fusion_alpha` numeric
- `fused_anomaly_score` numeric
- `caution_threshold_applied` numeric
- `lockout_threshold_applied` numeric
- `score_band` enum: `safe`, `caution`, `lockout`
- `scored_at` timestamptz

Notes:

- Thresholds should be persisted on the record used for the decision, not inferred later from mutable config.
- This table is the main analytical source for the threat feed.
- Column names should stay model-agnostic so the persistence layer does not hard-code AutoEncoder or Isolation Forest terminology.

### `policy_decisions`

Purpose:
Stores the policy outcome derived from a score and the tenant operating mode.

Suggested fields:

- `id` UUID primary key
- `tenant_id` UUID foreign key to `tenants`
- `auth_event_id` UUID foreign key to `auth_events`
- `risk_score_id` UUID foreign key to `risk_scores`
- `operating_mode_id` UUID foreign key to `tenant_operating_modes`
- `decision_band` enum: `safe`, `caution`, `lockout`
- `recommended_action` enum: `allow`, `step_up_mfa`, `terminate_session`, `lock_account`, `alert_only`
- `final_action` enum: `allow`, `step_up_mfa`, `terminate_session`, `lock_account`, `alert_only`, `none`
- `decision_reason` text nullable
- `decision_metadata` jsonb nullable
- `decided_at` timestamptz

Notes:

- `recommended_action` reflects policy logic.
- `final_action` reflects what the system actually chose under the active mode.

### `enforcement_actions`

Purpose:
Stores outbound enforcement attempts and their result history.

Suggested fields:

- `id` UUID primary key
- `tenant_id` UUID foreign key to `tenants`
- `policy_decision_id` UUID foreign key to `policy_decisions`
- `event_source_id` UUID foreign key to `event_sources` nullable
- `action_type` enum: `step_up_mfa`, `terminate_session`, `lock_account`
- `target_user_hash` text
- `integration_name` text
- `request_payload_redacted` jsonb nullable
- `status` enum: `pending`, `sent`, `succeeded`, `failed`, `skipped`
- `attempt_count` integer
- `external_action_id` text nullable
- `error_code` text nullable
- `error_message` text nullable
- `requested_at` timestamptz
- `completed_at` timestamptz nullable
- `created_at` timestamptz

Notes:

- This is deliberately separate from policy decisions because a decision may exist without any enforcement in `shadow` or `alert_only` mode.

### `alerts`

Purpose:
Stores analyst-visible alert records when the platform emits a notification or promotes a finding.

Suggested fields:

- `id` UUID primary key
- `tenant_id` UUID foreign key to `tenants`
- `policy_decision_id` UUID foreign key to `policy_decisions`
- `risk_score_id` UUID foreign key to `risk_scores`
- `severity` enum: `low`, `medium`, `high`
- `status` enum: `open`, `acknowledged`, `resolved`
- `title` text
- `summary` text
- `alert_metadata` jsonb nullable
- `created_at` timestamptz
- `acknowledged_at` timestamptz nullable
- `resolved_at` timestamptz nullable

Notes:

- This table is part of the MVP.
- It gives the dashboard a stable analyst-facing record separate from raw score history.

## Core Relationships

- one `tenant` has many `event_sources`
- one `tenant` has many `ingestion_credentials`
- one `tenant` has many `auth_events`
- one `auth_event` has many `event_processing_runs`
- one `auth_event` has zero or many `feature_snapshots`
- one `auth_event` has zero or many `host_interaction_snapshots`
- one `auth_event` has zero or many `risk_scores`
- one `risk_score` usually leads to one `policy_decision`
- one `policy_decision` may lead to zero or many `enforcement_actions`
- one `policy_decision` may lead to zero or one `alert` in the initial model

## Suggested Constraints and Indexes

### Uniqueness

- `tenants.slug`
- `ingestion_credentials.key_id`
- `tenant_hash_key_versions (tenant_id, key_version)`
- `auth_events (tenant_id, idempotency_key)`
- `host_interaction_snapshots (tenant_id, auth_event_id, processing_run_id, user_hash, host_hash)`
- optionally `auth_events (tenant_id, event_source_id, source_event_id)` when `source_event_id` is present

### Foreign-key and integrity rules

- all operational tables should carry `tenant_id`
- foreign-key chains should preserve tenant scoping in the application layer
- only one active operating mode per tenant
- only one active threshold profile per tenant
- only one active hash key version per tenant

### Query indexes

Prioritize indexes for:

- `auth_events (tenant_id, occurred_at desc)`
- `auth_events (tenant_id, user_hash, occurred_at desc)`
- `auth_events (tenant_id, outcome, occurred_at desc)`
- `risk_scores (tenant_id, scored_at desc)`
- `risk_scores (tenant_id, score_band, scored_at desc)`
- `host_interaction_snapshots (tenant_id, user_hash, window_end desc)`
- `host_interaction_snapshots (tenant_id, host_hash, window_end desc)`
- `policy_decisions (tenant_id, decided_at desc)`
- `enforcement_actions (tenant_id, status, requested_at desc)`
- `event_processing_runs (tenant_id, status, queued_at desc)`

## Canonical Event Shape Implications

The database design assumes the normalized authentication event schema will include, at minimum:

- tenant identity
- source-system identity
- event identity or idempotency identity
- occurrence timestamp
- outcome
- hashed user identity
- optional hashed session, host, device, and source IP identities
- authentication method
- optional failure reason
- optional coarse location context

If the canonical event schema grows, prefer extending `auth_events` only when the new field is operationally central. Less-stable source-specific fields should remain in redacted JSON metadata.

## Graph Feature Strategy

The research model includes graph-derived behavior such as `degree_centrality`, so inference cannot rely on the `auth_events` table alone if we want parity with the paper.

This draft therefore does not recommend omitting graph-support persistence entirely. Instead, it recommends avoiding a broad generic graph subsystem in the first iteration and using this narrower approach:

1. persist normalized `auth_events` as the source of truth
2. compute time-bounded user-host interaction aggregates during worker processing
3. store those aggregates in `host_interaction_snapshots`
4. rebuild the local graph view for the relevant tenant and scoring window when deriving graph features
5. persist the resulting scalar graph feature values in `feature_snapshots`

This gives the worker a practical way to calculate graph features for inference while keeping the MVP schema compact.

Concurrency implication:

- concurrent ingestion requests should only create `auth_events`
- they should not attempt to increment `interaction_count` directly
- `interaction_count` should be derived inside worker processing from the selected event window, which keeps the model retry-safe and avoids lost-update problems

Tradeoff:

- a full edge-history graph model would be more flexible for future graph analytics
- the snapshot approach is simpler and sufficient for the current model if windowed recomputation costs stay acceptable

If later testing shows that recomputing graph windows from events plus snapshots is too expensive or too awkward, we should promote `host_interaction_snapshots` into a fuller graph-edge history table in a follow-up schema revision.

## Deliberate Omissions From The First Draft

These are intentionally not first-class tables yet:

- user profile tables with reversible identities
- generic integration registry abstractions beyond simple source records
- broad incident/case-management workflows
- multi-region or high-volume partitioning strategies

Those can be added later if the implementation demonstrates a real need.

## Recommended Implementation Order

1. confirm this draft
2. define canonical event DTOs in `shared/schemas`
3. define domain entities and enums in `shared/domain`
4. implement SQLAlchemy models in `shared/database`
5. create the initial Alembic migration in `infra/migrations`

## Review Questions

Please review these choices before implementation:

1. Are the proposed enum sets correct enough to codify now, or do you want any additional states before we implement them in `shared/domain` and `shared/database`?
2. Is the `host_interaction_snapshots` approach acceptable for MVP graph-feature support, or do you want a fuller graph-edge history table from the start?
