# Alembic Scaffold

This directory is reserved for Alembic migration scripts and configuration.

The actual migration environment should import metadata from `shared/database` once the persistence layer is implemented.

Expected future contents:

- `alembic.ini`
- `env.py`
- `script.py.mako`
- `versions/`
