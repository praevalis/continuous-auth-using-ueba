from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from domain.tenant import (
	EventPayloadFormat,
	EventSourceStatus,
	EventSourceType,
	IngestionCredentialStatus,
	IngestionCredentialType,
	OperatingMode,
	TenantStatus,
)
from pydantic import Field, field_validator

from schemas.base import SchemaModel


class TenantSchema(SchemaModel):
	id: UUID
	slug: str = Field(min_length=1)
	display_name: str = Field(min_length=1)
	status: TenantStatus
	default_timezone: str = Field(min_length=1)
	deleted_at: datetime | None = None
	created_at: datetime
	updated_at: datetime


class TenantCreateSchema(SchemaModel):
	display_name: str = Field(min_length=1)
	default_timezone: str = Field(min_length=1)

	@field_validator('default_timezone')
	@classmethod
	def validate_timezone(cls, value: str) -> str:
		"""Validate that the configured timezone is recognized.

		Args:
			value: The timezone string to validate.

		Returns:
			The validated timezone string.

		Raises:
			ValueError: If the timezone is not recognized.
		"""
		try:
			ZoneInfo(value)
		except ZoneInfoNotFoundError as error:
			raise ValueError('Unsupported timezone value.') from error

		return value


class TenantUpdateSchema(SchemaModel):
	display_name: str | None = Field(default=None, min_length=1)
	default_timezone: str | None = Field(default=None, min_length=1)
	status: TenantStatus | None = None

	@field_validator('default_timezone')
	@classmethod
	def validate_optional_timezone(cls, value: str | None) -> str | None:
		"""Validate that the configured timezone is recognized when provided.

		Args:
			value: The optional timezone string to validate.

		Returns:
			The validated timezone string.

		Raises:
			ValueError: If the timezone is not recognized.
		"""
		if value is None:
			return value

		try:
			ZoneInfo(value)
		except ZoneInfoNotFoundError as error:
			raise ValueError('Unsupported timezone value.') from error

		return value


class TenantFilterParams(SchemaModel):
	slug: str | None = Field(default=None, min_length=1)
	display_name: str | None = Field(default=None, min_length=1)
	status: TenantStatus | None = None
	include_deleted: bool = False


class TenantOperatingModeSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	mode: OperatingMode
	is_active: bool
	effective_from: datetime
	effective_to: datetime | None = None
	changed_by: str | None = None
	change_reason: str | None = None
	created_at: datetime


class TenantOperatingModeCreateSchema(SchemaModel):
	mode: OperatingMode
	effective_from: datetime
	effective_to: datetime | None = None
	changed_by: str | None = None
	change_reason: str | None = None


class TenantOperatingModeRetireSchema(SchemaModel):
	effective_to: datetime | None = None
	changed_by: str | None = None
	change_reason: str | None = None


class TenantOperatingModeUpdateSchema(SchemaModel):
	mode: OperatingMode | None = None
	is_active: bool | None = None
	effective_from: datetime | None = None
	effective_to: datetime | None = None
	changed_by: str | None = None
	change_reason: str | None = None


class TenantOperatingModeFilterParams(SchemaModel):
	mode: OperatingMode | None = None
	is_active: bool | None = None


class TenantThresholdProfileSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	name: str = Field(min_length=1)
	description: str | None = None
	caution_threshold: float
	lockout_threshold: float
	fusion_alpha: float | None = None
	is_active: bool
	effective_from: datetime
	effective_to: datetime | None = None
	created_at: datetime
	updated_at: datetime


class TenantThresholdProfileCreateSchema(SchemaModel):
	name: str = Field(min_length=1)
	description: str | None = None
	caution_threshold: float
	lockout_threshold: float
	fusion_alpha: float | None = None
	effective_from: datetime
	effective_to: datetime | None = None


class TenantThresholdProfileRetireSchema(SchemaModel):
	effective_to: datetime | None = None


class TenantThresholdProfileUpdateSchema(SchemaModel):
	name: str | None = Field(default=None, min_length=1)
	description: str | None = None
	caution_threshold: float | None = None
	lockout_threshold: float | None = None
	fusion_alpha: float | None = None
	is_active: bool | None = None
	effective_from: datetime | None = None
	effective_to: datetime | None = None


class TenantThresholdProfileFilterParams(SchemaModel):
	name: str | None = Field(default=None, min_length=1)
	is_active: bool | None = None


class TenantHashKeyVersionSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	key_version: int = Field(ge=1)
	algorithm: str = Field(min_length=1)
	salt_value: str = Field(min_length=1)
	is_active: bool
	effective_from: datetime
	effective_to: datetime | None = None
	created_at: datetime


class TenantHashKeyVersionCreateSchema(SchemaModel):
	key_version: int = Field(ge=1)
	algorithm: str = Field(min_length=1)
	salt_value: str = Field(min_length=1)
	effective_from: datetime
	effective_to: datetime | None = None


class TenantHashKeyVersionRetireSchema(SchemaModel):
	effective_to: datetime | None = None


class TenantHashKeyVersionUpdateSchema(SchemaModel):
	algorithm: str | None = Field(default=None, min_length=1)
	salt_value: str | None = Field(default=None, min_length=1)
	is_active: bool | None = None
	effective_from: datetime | None = None
	effective_to: datetime | None = None


class TenantHashKeyVersionFilterParams(SchemaModel):
	key_version: int | None = Field(default=None, ge=1)
	is_active: bool | None = None


class EventSourceSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	source_name: str = Field(min_length=1)
	source_type: EventSourceType
	payload_format: EventPayloadFormat | None = None
	vendor: str | None = None
	external_reference: str | None = None
	status: EventSourceStatus
	created_at: datetime
	updated_at: datetime


class EventSourceCreateSchema(SchemaModel):
	source_name: str = Field(min_length=1)
	source_type: EventSourceType
	payload_format: EventPayloadFormat | None = None
	vendor: str | None = None
	external_reference: str | None = None
	status: EventSourceStatus = EventSourceStatus.ACTIVE


class EventSourceUpdateSchema(SchemaModel):
	source_name: str | None = Field(default=None, min_length=1)
	source_type: EventSourceType | None = None
	payload_format: EventPayloadFormat | None = None
	vendor: str | None = None
	external_reference: str | None = None
	status: EventSourceStatus | None = None


class EventSourceMetadataUpdateSchema(SchemaModel):
	source_name: str | None = Field(default=None, min_length=1)
	source_type: EventSourceType | None = None
	payload_format: EventPayloadFormat | None = None
	vendor: str | None = None
	external_reference: str | None = None


class EventSourceFilterParams(SchemaModel):
	source_type: EventSourceType | None = None
	payload_format: EventPayloadFormat | None = None
	status: EventSourceStatus | None = None
	vendor: str | None = None


class IngestionCredentialSchema(SchemaModel):
	id: UUID
	tenant_id: UUID
	event_source_id: UUID | None = None
	credential_name: str = Field(min_length=1)
	credential_type: IngestionCredentialType
	key_id: str = Field(min_length=1)
	key_hash: str = Field(min_length=1)
	status: IngestionCredentialStatus
	expires_at: datetime | None = None
	last_used_at: datetime | None = None
	created_at: datetime
	rotated_at: datetime | None = None


class IngestionCredentialCreateSchema(SchemaModel):
	credential_name: str = Field(min_length=1)
	event_source_id: UUID | None = None
	credential_type: IngestionCredentialType = IngestionCredentialType.API_KEY
	expires_at: datetime | None = None


class IngestionCredentialUpdateSchema(SchemaModel):
	credential_name: str | None = Field(default=None, min_length=1)
	event_source_id: UUID | None = None
	key_id: str | None = Field(default=None, min_length=1)
	key_hash: str | None = Field(default=None, min_length=1)
	status: IngestionCredentialStatus | None = None
	expires_at: datetime | None = None
	last_used_at: datetime | None = None
	rotated_at: datetime | None = None


class IngestionCredentialMetadataUpdateSchema(SchemaModel):
	credential_name: str | None = Field(default=None, min_length=1)
	event_source_id: UUID | None = None
	expires_at: datetime | None = None


class IngestionCredentialFilterParams(SchemaModel):
	event_source_id: UUID | None = None
	credential_type: IngestionCredentialType | None = None
	status: IngestionCredentialStatus | None = None


class IssuedIngestionCredentialSchema(SchemaModel):
	credential: IngestionCredentialSchema
	plaintext_secret: str = Field(min_length=1)
