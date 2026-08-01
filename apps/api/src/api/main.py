from fastapi import FastAPI

from api.core.config import get_api_settings
from api.core.errors import register_exception_handlers
from api.core.lifespan import lifespan
from api.core.middleware import register_middlewares
from api.routes import register_routes


def create_application() -> FastAPI:
	"""Create and configure the FastAPI application.

	Returns:
		The configured FastAPI application instance.
	"""
	settings = get_api_settings()
	app = FastAPI(
		title='Continuous Authentication API',
		lifespan=lifespan,
	)

	register_middlewares(app, settings)
	register_exception_handlers(app)
	register_routes(app)

	return app


app = create_application()
