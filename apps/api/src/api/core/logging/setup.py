import logging


def configure_logging(log_level: str) -> None:
	"""Configure application logging.

	Args:
		log_level: The root log level to apply.
	"""
	logging.basicConfig(
		level=getattr(logging, log_level.upper(), logging.INFO),
		format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
		force=True,
	)
	logging.captureWarnings(True)
