from enum import StrEnum


class AuthEventOutcome(StrEnum):
	SUCCESS = 'success'
	FAILURE = 'failure'
	CHALLENGE = 'challenge'
	LOGOUT = 'logout'
	UNKNOWN = 'unknown'
