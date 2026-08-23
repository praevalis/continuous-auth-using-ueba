"""API routes package."""

from fastapi import APIRouter, FastAPI

from api.routes.alerts import router as alerts_router
from api.routes.enforcement import router as enforcement_router
from api.routes.events import router as events_router
from api.routes.health import router as health_router
from api.routes.ingestion import router as ingestion_router
from api.routes.integrations import router as integrations_router
from api.routes.policy_decisions import router as policy_decisions_router
from api.routes.risk_summary import router as risk_summary_router
from api.routes.tenant_configuration import router as tenant_configuration_router
from api.routes.tenants import router as tenants_router

api_router = APIRouter()
api_router.include_router(alerts_router)
api_router.include_router(events_router)
api_router.include_router(enforcement_router)
api_router.include_router(health_router)
api_router.include_router(tenants_router)
api_router.include_router(tenant_configuration_router)
api_router.include_router(ingestion_router)
api_router.include_router(integrations_router)
api_router.include_router(policy_decisions_router)
api_router.include_router(risk_summary_router)


def register_routes(app: FastAPI) -> None:
	"""Register the API route tree on the application.

	Args:
		app: The FastAPI application instance.
	"""
	app.include_router(api_router)


__all__ = ['api_router', 'register_routes']
