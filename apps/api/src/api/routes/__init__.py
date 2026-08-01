"""API routes package."""

from fastapi import APIRouter, FastAPI

from api.routes.auth import router as auth_router
from api.routes.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)


def register_routes(app: FastAPI) -> None:
	"""Register the API route tree on the application.

	Args:
		app: The FastAPI application instance.
	"""
	app.include_router(api_router)


__all__ = ['api_router', 'register_routes']
