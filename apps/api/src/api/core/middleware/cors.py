from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import ApiSettings


def add_cors_middleware(app: FastAPI, settings: ApiSettings) -> None:
	"""Register the FastAPI CORS middleware.

	Args:
		app: The FastAPI application instance.
		settings: The resolved API settings used to configure CORS behavior.
	"""
	app.add_middleware(
		CORSMiddleware,
		allow_origins=settings.API_CORS_ALLOW_ORIGINS,
		allow_credentials=settings.API_CORS_ALLOW_CREDENTIALS,
		allow_methods=settings.API_CORS_ALLOW_METHODS,
		allow_headers=settings.API_CORS_ALLOW_HEADERS,
	)
