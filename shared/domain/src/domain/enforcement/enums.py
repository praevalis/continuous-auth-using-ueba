from enum import StrEnum


class EnforcementActionType(StrEnum):
	STEP_UP_MFA = 'step_up_mfa'
	TERMINATE_SESSION = 'terminate_session'
	LOCK_ACCOUNT = 'lock_account'


class EnforcementActionStatus(StrEnum):
	PENDING = 'pending'
	SENT = 'sent'
	SUCCEEDED = 'succeeded'
	FAILED = 'failed'
	SKIPPED = 'skipped'
