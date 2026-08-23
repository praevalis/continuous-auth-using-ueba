from schemas.base import SchemaModel
from schemas.event import AuthEventListItemSchema

from api.core.pagination import OffsetPaginationSchema


class AuthEventListResponseSchema(SchemaModel):
	items: list[AuthEventListItemSchema]
	pagination: OffsetPaginationSchema
