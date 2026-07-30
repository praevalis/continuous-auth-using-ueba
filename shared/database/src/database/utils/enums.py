from enum import Enum

from sqlalchemy import Enum as SQLEnum


def enum_type(enum_cls: type[Enum], *, name: str) -> SQLEnum:
	"""Create a SQLAlchemy enum type from a Python enum.

	Args:
		enum_cls: The Python enum class to map.
		name: The database enum type name.

	Returns:
		A SQLAlchemy enum type configured to persist enum values.
	"""
	return SQLEnum(
		enum_cls,
		name=name,
		values_callable=lambda values: [item.value for item in values],
	)


__all__ = ['enum_type']
