from enum import StrEnum


class ScoreBand(StrEnum):
	SAFE = 'safe'
	CAUTION = 'caution'
	LOCKOUT = 'lockout'


class PolicyAction(StrEnum):
	ALLOW = 'allow'
	STEP_UP_MFA = 'step_up_mfa'
	TERMINATE_SESSION = 'terminate_session'
	LOCK_ACCOUNT = 'lock_account'
	ALERT_ONLY = 'alert_only'
	NONE = 'none'
