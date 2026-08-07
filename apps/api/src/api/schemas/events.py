from schemas.base import SchemaModel
from schemas.event import AuthEventSchema

from api.core.pagination import OffsetPaginationSchema


class AuthEventListResponseSchema(SchemaModel):
	items: list[AuthEventSchema]
	pagination: OffsetPaginationSchema
