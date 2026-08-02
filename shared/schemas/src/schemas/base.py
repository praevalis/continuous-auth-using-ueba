from pydantic import BaseModel, ConfigDict


class SchemaModel(BaseModel):
	"""Base class for shared DTOs."""

	model_config = ConfigDict(
		extra='forbid',
		frozen=False,
		from_attributes=True,
		populate_by_name=True,
		use_enum_values=False,
	)
