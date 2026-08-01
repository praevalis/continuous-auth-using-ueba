from fastapi import Request

from api.core.infrastructure import InfrastructureManager


def get_infrastructure_manager(request: Request) -> InfrastructureManager:
	"""Return the initialized infrastructure manager from application state.

	Args:
		request: The incoming FastAPI request.

	Returns:
		The initialized infrastructure manager stored on the application state.
	"""
	return request.app.state.infrastructure_manager
