from enum import StrEnum


class AlertSeverity(StrEnum):
	LOW = 'low'
	MEDIUM = 'medium'
	HIGH = 'high'


class AlertStatus(StrEnum):
	OPEN = 'open'
	ACKNOWLEDGED = 'acknowledged'
	RESOLVED = 'resolved'
