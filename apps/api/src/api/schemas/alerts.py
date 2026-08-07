from schemas.alert import AlertSchema
from schemas.base import SchemaModel

from api.core.pagination import OffsetPaginationSchema


class AlertListResponseSchema(SchemaModel):
	items: list[AlertSchema]
	pagination: OffsetPaginationSchema
