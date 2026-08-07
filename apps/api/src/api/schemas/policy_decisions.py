from schemas.base import SchemaModel
from schemas.policy import PolicyDecisionSchema

from api.core.pagination import OffsetPaginationSchema


class PolicyDecisionListResponseSchema(SchemaModel):
	items: list[PolicyDecisionSchema]
	pagination: OffsetPaginationSchema
