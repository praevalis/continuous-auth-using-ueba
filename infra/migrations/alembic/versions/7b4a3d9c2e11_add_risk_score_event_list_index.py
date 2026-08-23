"""add risk score event list index

Revision ID: 7b4a3d9c2e11
Revises: 1e93dba3a20f
Create Date: 2026-08-23 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '7b4a3d9c2e11'
down_revision: Union[str, Sequence[str], None] = '1e93dba3a20f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""Add the tenant-scoped latest-score lookup index."""
	op.create_index(
		op.f('ix_risk_scores_tenant_event_scored_at'),
		'risk_scores',
		['tenant_id', 'auth_event_id', 'scored_at'],
		unique=False,
	)


def downgrade() -> None:
	"""Remove the tenant-scoped latest-score lookup index."""
	op.drop_index(
		op.f('ix_risk_scores_tenant_event_scored_at'),
		table_name='risk_scores',
	)
