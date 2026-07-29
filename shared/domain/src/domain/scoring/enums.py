from enum import StrEnum


class ProcessingJobType(StrEnum):
	SCORE_EVENT = 'score_event'
	SEND_ALERT = 'send_alert'
	ENFORCE_ACTION = 'enforce_action'


class ProcessingRunStatus(StrEnum):
	QUEUED = 'queued'
	RUNNING = 'running'
	SUCCEEDED = 'succeeded'
	FAILED = 'failed'
	DEAD_LETTERED = 'dead_lettered'
