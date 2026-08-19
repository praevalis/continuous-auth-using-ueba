import type { components } from '@/api/generated/types';
import type { ActivityEntry, ActivityTone } from './types';

type Alert = components['schemas']['AlertSchema'];
type PolicyDecision = components['schemas']['PolicyDecisionSchema'];
type EnforcementAction = components['schemas']['EnforcementActionSchema'];

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
		time: alert.created_at,
		title: alert.title,
		user: 'User unavailable',
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
		time: decision.decided_at,
		title: `${decision.decision_band[0].toUpperCase()}${decision.decision_band.slice(1)} decision recorded`,
		user: 'User unavailable',
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
		time: action.completed_at ?? action.requested_at,
		title: actionTitle(action.action_type),
		user: 'User unavailable',
		status: displayActionStatus(action.status),
		statusTone:
			action.status === 'failed'
				? 'lockout'
				: action.status === 'skipped'
					? 'caution'
					: 'safe',
	};
}
