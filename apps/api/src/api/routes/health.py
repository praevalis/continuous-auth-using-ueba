from fastapi import APIRouter

router = APIRouter(prefix='/health', tags=['health'])


@router.get('', summary='Health check')
async def health_check() -> dict[str, str]:
	"""Return a basic liveness response.

	Returns:
		A simple liveness payload.
	"""
	return {'status': 'ok'}
