"""API routes package."""

from fastapi import APIRouter, FastAPI

from api.routes.health import router as health_router
from api.routes.ingestion import router as ingestion_router
from api.routes.tenant_configuration import router as tenant_configuration_router
from api.routes.tenants import router as tenants_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(tenants_router)
api_router.include_router(tenant_configuration_router)
api_router.include_router(ingestion_router)


def register_routes(app: FastAPI) -> None:
	"""Register the API route tree on the application.

	Args:
		app: The FastAPI application instance.
	"""
	app.include_router(api_router)


__all__ = ['api_router', 'register_routes']
