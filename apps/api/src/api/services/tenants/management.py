from uuid import UUID

from database import IUnitOfWork
from schemas.tenant import (
	TenantFilterParams,
	TenantSchema,
	TenantUpdateSchema,
)


class TenantManagementService:
	def __init__(self, uow: IUnitOfWork) -> None:
		"""Initialize the tenant management service.

		Args:
			uow: The request-scoped database unit of work.
		"""
		self._uow = uow

	async def list_tenants(
		self,
		filters: TenantFilterParams,
	) -> list[TenantSchema]:
		"""Return tenants matching the provided filters.

		Args:
			filters: Tenant filter parameters.

		Returns:
			The tenant response schemas matching the provided filters.
		"""
		tenant_models = await self._uow.tenants.list_tenants(filters)
		return [
			TenantSchema.model_validate(tenant_model) for tenant_model in tenant_models
		]

	async def get_tenant(self, tenant_id: UUID) -> TenantSchema:
		"""Return an active tenant by identifier.

		Args:
			tenant_id: The tenant identifier.

		Returns:
			The matching tenant response schema.
		"""
		tenant_model = await self._uow.tenants.get_active_tenant_by_id_or_raise(
			tenant_id
		)
		return TenantSchema.model_validate(tenant_model)

	async def update_tenant(
		self,
		tenant_id: UUID,
		payload: TenantUpdateSchema,
	) -> TenantSchema:
		"""Update an active tenant.

		Args:
			tenant_id: The tenant identifier.
			payload: The tenant update payload.

		Returns:
			The updated tenant response schema.
		"""
		tenant_model = await self._uow.tenants.update_tenant(tenant_id, payload)
		await self._uow.commit()
		return TenantSchema.model_validate(tenant_model)

	async def delete_tenant(self, tenant_id: UUID) -> None:
		"""Soft delete an active tenant.

		Args:
			tenant_id: The tenant identifier.
		"""
		await self._uow.tenants.delete_tenant(tenant_id)
		await self._uow.commit()
