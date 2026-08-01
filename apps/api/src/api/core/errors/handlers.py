import logging

from domain import DomainError
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.core.errors.mapping import get_domain_error_mapping

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
	"""Register application exception handlers.

	Args:
		app: The FastAPI application instance.
	"""

	@app.exception_handler(DomainError)
	async def handle_domain_error(
		request: Request,
		exc: DomainError,
	) -> JSONResponse:
		"""Return a structured response for domain-layer errors.

		Args:
			request: The inbound request associated with the exception.
			exc: The raised domain exception.

		Returns:
			A JSON response describing the domain error.
		"""
		_ = request
		mapping = get_domain_error_mapping(exc)

		return JSONResponse(
			status_code=mapping.status_code,
			content={
				'error': {
					'code': mapping.error_code,
					'message': str(exc),
				},
			},
		)

	@app.exception_handler(RequestValidationError)
	async def handle_request_validation_error(
		request: Request,
		exc: RequestValidationError,
	) -> JSONResponse:
		"""Return a structured response for request validation errors.

		Args:
			request: The inbound request associated with the exception.
			exc: The raised request validation error.

		Returns:
			A JSON response describing the validation failure.
		"""
		_ = request
		return JSONResponse(
			status_code=422,
			content={
				'error': {
					'code': 'request_validation_error',
					'message': 'Request validation failed.',
					'details': exc.errors(),
				},
			},
		)

	@app.exception_handler(Exception)
	async def handle_unexpected_error(
		request: Request,
		exc: Exception,
	) -> JSONResponse:
		"""Return a structured response for unexpected application errors.

		Args:
			request: The inbound request associated with the exception.
			exc: The unexpected exception.

		Returns:
			A generic internal server error response.
		"""
		logger.exception(
			'Unhandled exception while processing request.',
			extra={
				'request_method': request.method,
				'request_path': request.url.path,
			},
		)

		return JSONResponse(
			status_code=500,
			content={
				'error': {
					'code': 'internal_server_error',
					'message': 'An unexpected error occurred.',
				},
			},
		)
