import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = 'X-Request-ID'
logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next) -> Response:
		"""Attach a request ID, log the request, and propagate the response header.

		Args:
			request: The inbound ASGI request.
			call_next: The downstream request handler.

		Returns:
			The outgoing response with the request ID header attached.
		"""
		request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
		request.state.request_id = request_id

		start_time = perf_counter()
		response = await call_next(request)
		duration_ms = round((perf_counter() - start_time) * 1000, 2)

		response.headers[REQUEST_ID_HEADER] = request_id
		logger.info(
			'Request completed.',
			extra={
				'request_id': request_id,
				'request_method': request.method,
				'request_path': request.url.path,
				'response_status_code': response.status_code,
				'duration_ms': duration_ms,
			},
		)

		return response


def add_request_context_middleware(app: FastAPI) -> None:
	"""Register the request context middleware.

	Args:
		app: The FastAPI application instance.
	"""
	app.add_middleware(RequestContextMiddleware)
