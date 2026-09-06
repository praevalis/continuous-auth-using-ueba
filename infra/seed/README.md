# Seed data and loaders

This directory contains reproducible seed inputs and loaders for the Continuous
Auth platform. The data is kept in JSON so the loaders remain focused on
endpoint and persistence orchestration.

## Files

- `seed-data.json` — the single source of truth, split into `api` inputs and
  deterministic `database` records.
- `seed_api.py` — creates API-owned resources and submits the ingestion event.
- `seed_database.py` — loads dashboard records through the shared SQLAlchemy
  models using logical JSON keys and deterministic IDs.
- `seed_platform.py` — runs both existing seed stages as one ephemeral Docker
  Compose operation.
- `keycloak-seed-data.json` contains deterministic realm, service-client, and
  demo-user configuration for the local Keycloak instance.
- `seed_keycloak.py` configures Keycloak through its Admin API, tests the seeded
  tenant connection, and activates it.
- `seed-state.json` — generated locally with API-created IDs and the issued
  ingestion secret. It is ignored by Git.

## Seed order

`seed_api.py` validates the real runtime path:

1. Create or reuse the global provider registry entry.
2. Onboard the tenant, including its initial operating mode, threshold profile, and hash-key version.
3. Create or reuse the event source, ingestion credential, and provider connection.
4. Submit the replay event through the ingestion endpoint.

`seed_database.py` then loads the complete dashboard dataset:

1. Authentication events.
2. Processing runs.
3. Feature and host-interaction snapshots.
4. Risk scores across safe, caution, and lockout bands.
5. Policy decisions.
6. Alerts across lifecycle states.
7. Enforcement actions across skipped and succeeded states.

After the platform seed completes, `seed_keycloak.py` configures the local IdP:

1. Create or update the `demo` realm.
2. Create or update the outbound-enforcement service client.
3. Grant its service account the required realm-management roles.
4. Create or update the demonstration user and password.
5. Update, test, and activate the seeded tenant provider connection.

The Keycloak administrator, database, service-client, and demo-user credentials
are intentionally static and development-only. The service-client secret is
referenced by name in platform data and is available to the API and worker only
through the local Compose environment.

The API loader and database loader are intentionally separate. The first
validates the production-shaped workflow; the second provides deterministic
coverage for frontend demonstrations without waiting for enough natural events.

The database fixture contains 20 scored events selected from the `baseline-v4`
held-out evaluation window. Their version-2 feature snapshots and model scores
are preserved in `seed-data.json`, then shifted by whole weeks to August 29
through September 1, 2026. This preserves their weekday features while keeping
them inside the reference environment's 30-day dashboard filters.
The fixture is deliberately stratified as 15 safe, 4 caution, and 1 lockout
event (75% / 20% / 5%). This distribution provides useful UI coverage; it is
not intended to reproduce the naturally imbalanced evaluation distribution.
The API stage submits one additional replay event through the live ingestion
and worker path. `seed_api.py` replaces its fixture timestamp with the current
UTC time so the event occurs after the tenant configuration becomes effective.
Its eventual score depends on worker processing and is not included in the
fixed 75% / 20% / 5% database-fixture distribution.

## Running

Docker Compose runs migrations and all seed stages automatically:

```bash
docker compose up -d --build
```

The local Keycloak administration console is available at
`http://localhost:8081` with `admin` / `admin`. The seeded `demo` realm includes
`demo.alice@example.test` with password `demo`. These credentials are
development-only.

The startup dependency order is:

```text
PostgreSQL -> migrate -> API -> platform-seed
                    \-> worker       \
                                      -> keycloak-seed
Keycloak PostgreSQL -> Keycloak -----/
```

`platform-seed` uses a temporary state file inside its container, runs
`seed_api.py` first, waits for the worker to persist the replay event, and then
runs `seed_database.py`. Inspect one-shot service output with:

```bash
docker compose logs migrate platform-seed keycloak-seed
```

For a manual host-side seed, start the API, worker, PostgreSQL, and Redis first.
From the repository root, run the API loader:

```bash
python ./infra/seed/seed_api.py --wait-for-worker
```

After the API loader has created `seed-state.json`, run the database loader with
the repository environment configured for PostgreSQL:

```bash
python ./infra/seed/seed_database.py
```

Options:

```text
--base-url URL                 API URL; defaults to http://localhost:8000
--seed-file PATH               Alternate seed data file (both loaders)
--state-file PATH              Alternate generated state file (both loaders)
--wait-for-worker              Poll until the event is visible through the API
--worker-wait-seconds SECONDS  Poll timeout; defaults to 20
```

For example:

```powershell
python .\infra\seed\seed_api.py `
  --base-url http://localhost:8000 `
  --wait-for-worker `
  --worker-wait-seconds 30
```

The tenant remains in `shadow` mode even though `seed_keycloak.py` activates the
provider connection. It therefore records decisions without dispatching live
provider actions during normal startup. Do not commit or share the generated
`seed-state.json`, because it contains the ingestion secret.

The loaders are idempotent and do not overwrite existing records. After a
fixture definition or threshold changes, recreate the local database (or remove
the prior seed records) before rerunning both stages if you need the database to
match the current fixture exactly.
