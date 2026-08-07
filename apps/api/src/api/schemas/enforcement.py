from schemas.base import SchemaModel
from schemas.enforcement import EnforcementActionSchema

from api.core.pagination import OffsetPaginationSchema


class EnforcementActionListResponseSchema(SchemaModel):
	items: list[EnforcementActionSchema]
	pagination: OffsetPaginationSchema
