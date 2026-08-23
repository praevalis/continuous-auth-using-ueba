import type {
	AuthEvent,
	AuthEventDetail,
	AuthEventListItem,
	PolicyDecision,
} from '@/api/contracts';
import { formatTimestamp } from '@/utils';
import type { ThreatEvent } from './types';

function displayLabel(value: string) {
	return value
		.split('_')
		.map((part) => part.charAt(0).toUpperCase() + part.slice(1))
		.join(' ');
}

function displayNumber(value: number | null | undefined) {
	return value === null || value === undefined
		? 'Not available'
		: value.toFixed(2);
}

function riskTone(
	band: PolicyDecision['decision_band'] | undefined,
): ThreatEvent['tone'] {
	return band ?? 'unknown';
}

function resultLabel(outcome: AuthEvent['outcome']): ThreatEvent['result'] {
	if (outcome === 'success') return 'Success';
	if (outcome === 'failure') return 'Failed';
	if (outcome === 'challenge') return 'Challenge';
	if (outcome === 'logout') return 'Signed out';
	return 'Unknown';
}

function responseLabel(decision?: PolicyDecision) {
	if (!decision) return 'Not evaluated';
	return {
		allow: 'Allow sign-in',
		step_up_mfa: 'Ask for extra verification',
		terminate_session: 'End session',
		lock_account: 'Lock account',
		alert_only: 'Create alert',
		none: 'No action taken',
	}[decision.final_action];
}

function responseStatus(detail?: AuthEventDetail) {
	if (!detail?.policy_decision) return 'Not evaluated';
	const actions = detail.enforcement_actions ?? [];
	if (actions.length === 0) return 'Recorded';
	if (actions.some((action) => action.status === 'failed')) return 'Failed';
	if (actions.every((action) => action.status === 'succeeded'))
		return 'Success';
	return displayLabel(actions[0].status);
}

function observedSignals(
	detail?: AuthEventDetail,
): ThreatEvent['observedSignals'] {
	const features = detail?.feature_snapshot;
	if (!features) return [];
	return [
		['Login frequency', displayNumber(features.login_frequency)],
		['Average inter-event time', displayNumber(features.avg_inter_event_time)],
		['Time since last login', displayNumber(features.time_since_last_login)],
		['Unique hosts', displayNumber(features.unique_hosts)],
		['Host entropy', displayNumber(features.host_entropy)],
		['Top host ratio', displayNumber(features.top_host_ratio)],
		['Degree centrality', displayNumber(features.degree_centrality)],
	].map(([label, observed]) => ({
		label,
		observed,
		baseline: 'Not available',
	}));
}

function responseActivity(
	detail?: AuthEventDetail,
): ThreatEvent['responseActivity'] {
	if (!detail) return [];
	const activity: ThreatEvent['responseActivity'] = [];
	const addActivity = (id: string, dateTime: string, label: string) => {
		activity.push({
			id,
			dateTime,
			time: formatTimestamp(dateTime),
			label,
		});
	};
	const run = detail.processing_run;
	if (run) {
		addActivity(`${run.id}-queued`, run.queued_at, 'Processing queued');
		if (run.started_at)
			addActivity(`${run.id}-started`, run.started_at, 'Processing started');
		if (run.finished_at)
			addActivity(
				`${run.id}-finished`,
				run.finished_at,
				`Processing ${displayLabel(run.status)}`,
			);
	}
	if (detail.policy_decision) {
		addActivity(
			detail.policy_decision.id,
			detail.policy_decision.decided_at,
			'Policy decision recorded',
		);
	}
	for (const alert of detail.alerts ?? []) {
		addActivity(alert.id, alert.created_at, 'Alert created');
	}
	for (const action of detail.enforcement_actions ?? []) {
		addActivity(
			`${action.id}-requested`,
			action.requested_at,
			`${displayLabel(action.action_type)} requested`,
		);
		if (action.completed_at)
			addActivity(
				`${action.id}-completed`,
				action.completed_at,
				`${displayLabel(action.action_type)} completed`,
			);
	}
	return activity.sort((left, right) =>
		left.dateTime.localeCompare(right.dateTime),
	);
}

export function mapThreatEvent(
	event: AuthEventListItem,
	decision?: PolicyDecision,
	detail?: AuthEventDetail,
): ThreatEvent {
	const score = detail?.risk_score ?? event.risk_score;
	const selectedDecision = detail?.policy_decision ?? decision;
	const band = score?.score_band ?? selectedDecision?.decision_band;
	return {
		id: event.id,
		dateTime: event.occurred_at,
		time: formatTimestamp(event.occurred_at),
		initials: event.user_hash.slice(0, 2).toUpperCase(),
		user: `User ${event.user_hash.slice(0, 8)}`,
		signInType: displayLabel(event.event_type),
		result: resultLabel(event.outcome),
		risk: band ? (displayLabel(band) as ThreatEvent['risk']) : 'Unknown',
		tone: riskTone(band),
		score: score?.fused_anomaly_score ?? null,
		cautionThreshold: score?.caution_threshold_applied ?? null,
		lockoutThreshold: score?.lockout_threshold_applied ?? null,
		response: responseLabel(selectedDecision),
		decisionStatus: selectedDecision ? 'Recorded' : 'Not evaluated',
		decisionNote:
			selectedDecision?.decision_reason ?? 'No policy decision recorded.',
		responseStatus: responseStatus(detail),
		device: event.device_hash
			? `Device ${event.device_hash.slice(0, 8)}`
			: 'Not available',
		network: event.source_ip_prefix ?? 'Redacted',
		observedSignals: observedSignals(detail),
		responseActivity: responseActivity(detail),
	};
}
