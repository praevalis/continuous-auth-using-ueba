from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.tenant.enums import OperatingMode, TenantStatus


@dataclass(slots=True)
class Tenant:
	id: UUID
	slug: str
	display_name: str
	status: TenantStatus
	default_timezone: str
	created_at: datetime
	updated_at: datetime


@dataclass(slots=True)
class TenantOperatingModeRecord:
	id: UUID
	tenant_id: UUID
	mode: OperatingMode
	is_active: bool
	effective_from: datetime
	effective_to: datetime | None
	changed_by: str | None
	change_reason: str | None
	created_at: datetime


@dataclass(slots=True)
class TenantThresholdProfile:
	id: UUID
	tenant_id: UUID
	name: str
	description: str | None
	caution_threshold: float
	lockout_threshold: float
	fusion_alpha: float | None
	is_active: bool
	effective_from: datetime
	effective_to: datetime | None
	created_at: datetime
	updated_at: datetime


@dataclass(slots=True)
class TenantHashKeyVersion:
	id: UUID
	tenant_id: UUID
	key_version: int
	algorithm: str
	salt_value: str
	is_active: bool
	effective_from: datetime
	effective_to: datetime | None
	created_at: datetime
