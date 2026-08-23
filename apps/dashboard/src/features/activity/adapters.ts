import type { Alert, EnforcementAction, PolicyDecision } from '@/api/contracts';
import { formatTimestamp } from '@/utils';
import type { ActivityEntry, ActivityTone } from './types';

function toneFromBand(band: PolicyDecision['decision_band']): ActivityTone {
	return band;
}

function toneFromSeverity(severity: Alert['severity']): ActivityTone {
	if (severity === 'high') return 'lockout';
	if (severity === 'medium') return 'caution';
	return 'safe';
}

function displayAlertStatus(status: Alert['status']): ActivityEntry['status'] {
	return (status[0].toUpperCase() + status.slice(1)) as ActivityEntry['status'];
}

function displayActionStatus(
	status: EnforcementAction['status'],
): ActivityEntry['status'] {
	return (status[0].toUpperCase() + status.slice(1)) as ActivityEntry['status'];
}

function displayPolicyAction(action: PolicyDecision['final_action']) {
	return {
		allow: 'Allow sign-in',
		step_up_mfa: 'Ask for extra verification',
		terminate_session: 'End session',
		lock_account: 'Lock account',
		alert_only: 'Create alert',
		none: 'No action taken',
	}[action];
}

function displayLabel(value: string) {
	return value
		.split('_')
		.map((part) => part.charAt(0).toUpperCase() + part.slice(1))
		.join(' ');
}

function actionTitle(action: EnforcementAction['action_type']) {
	return {
		step_up_mfa: 'Extra verification requested',
		terminate_session: 'End session',
		lock_account: 'Lock account',
	}[action];
}

/** Maps an API alert into the presentation model used by the activity stream. */
export function mapAlertToActivityEntry(alert: Alert): ActivityEntry {
	return {
		id: alert.id,
		dateTime: alert.created_at,
		time: formatTimestamp(alert.created_at),
		title: alert.title,
		context: alert.summary,
		status: displayAlertStatus(alert.status),
		statusTone: toneFromSeverity(alert.severity),
	};
}

/** Maps an API policy decision into the presentation model used by the activity stream. */
export function mapPolicyDecisionToActivityEntry(
	decision: PolicyDecision,
): ActivityEntry {
	return {
		id: decision.id,
		dateTime: decision.decided_at,
		time: formatTimestamp(decision.decided_at),
		title: `${decision.decision_band[0].toUpperCase()}${decision.decision_band.slice(1)} decision recorded`,
		context:
			decision.decision_reason ?? displayPolicyAction(decision.final_action),
		status: 'Recorded',
		statusTone: toneFromBand(decision.decision_band),
	};
}

/** Maps an API enforcement action into the presentation model used by the activity stream. */
export function mapEnforcementActionToActivityEntry(
	action: EnforcementAction,
): ActivityEntry {
	return {
		id: action.id,
		dateTime: action.completed_at ?? action.requested_at,
		time: formatTimestamp(action.completed_at ?? action.requested_at),
		title: actionTitle(action.action_type),
		context:
			action.status === 'failed' && action.error_message
				? action.error_message
				: displayLabel(action.integration_name),
		status: displayActionStatus(action.status),
		statusTone:
			action.status === 'failed'
				? 'lockout'
				: action.status === 'skipped'
					? 'caution'
					: 'safe',
	};
}
