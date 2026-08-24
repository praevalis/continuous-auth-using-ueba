import { LuDownload, LuSearch, LuShieldCheck } from 'react-icons/lu';
import type { IconType } from 'react-icons';
import type {
	Alert,
	AuthEventListItem,
	EnforcementAction,
	PipelineHealthComponent,
	PolicyDecision,
} from '@/api/contracts';
import { formatTimestamp } from '@/utils';
import type { OverviewData } from '@/hooks/useOverview';
import type {
	OverviewActivityItem,
	OverviewActivityTrace,
	OverviewChart,
	OverviewPlatformItem,
	OverviewRiskSegment,
	OverviewSystemActivityItem,
	OverviewTone,
	OverviewView,
} from './types';

const PLATFORM_CONFIG: Array<{
	component: PipelineHealthComponent['component'];
	icon: IconType;
	label: string;
}> = [
	{ component: 'ingestion', icon: LuDownload, label: 'Event intake' },
	{ component: 'analysis', icon: LuSearch, label: 'Analysis' },
	{ component: 'responses', icon: LuShieldCheck, label: 'Responses' },
];

const RISK_CONFIG = [
	{ label: 'Safe', className: 'bg-safe', tone: 'text-safe' },
	{ label: 'Caution', className: 'bg-caution', tone: 'text-caution' },
	{ label: 'Lockout', className: 'bg-lockout', tone: 'text-lockout' },
] as const;

function displayLabel(value: string) {
	return value
		.split('_')
		.map((part) => part.charAt(0).toUpperCase() + part.slice(1))
		.join(' ');
}

function statusLabel(status: PipelineHealthComponent['status']) {
	return {
		healthy: 'Healthy',
		degraded: 'Healthy',
		idle: 'Idle',
		not_configured: 'Not configured',
	}[status];
}

function statusTone(status: PipelineHealthComponent['status']): OverviewTone {
	if (status === 'healthy') return 'safe';
	if (status === 'degraded') return 'safe';
	return 'neutral';
}

function mapPlatformItems(data: OverviewData): OverviewPlatformItem[] {
	return PLATFORM_CONFIG.map(({ component, icon, label }) => {
		const health = data.pipelineHealth.components.find(
			(item) => item.component === component,
		);
		return {
			icon,
			label,
			status: health ? statusLabel(health.status) : 'Not available',
			updated: health?.last_activity_at
				? `Updated ${formatTimestamp(health.last_activity_at)}`
				: 'No activity yet',
			tone: health ? statusTone(health.status) : 'neutral',
		};
	});
}

function mapRiskSegments(data: OverviewData): OverviewRiskSegment[] {
	const counts = [
		data.riskSummary.safe_count,
		data.riskSummary.caution_count,
		data.riskSummary.lockout_count,
	];
	const total = counts.reduce((sum, count) => sum + count, 0);
	return RISK_CONFIG.map((config, index) => ({
		...config,
		value: `${total ? Math.round((counts[index] / total) * 100) : 0}%`,
	}));
}

function buildTrace(values: number[], color: string): OverviewActivityTrace {
	const width = 640;
	const baseline = 42;
	const amplitude = 34;
	const max = Math.max(...values, 1);
	const step = values.length > 1 ? width / (values.length - 1) : width;
	const points = values.map((value, index) => {
		const x = index * step;
		const y = baseline - (value / max) * amplitude;
		return `${x.toFixed(1)} ${y.toFixed(1)}`;
	});
	return { path: `M${points.join(' L')}`, color };
}

function chartLabel(value: string) {
	return new Intl.DateTimeFormat(undefined, {
		hour: '2-digit',
		minute: '2-digit',
	}).format(new Date(value));
}

function mapChart(data: OverviewData): OverviewChart {
	const buckets = data.activityTrend.buckets;
	const hasActivity = buckets.some((bucket) => bucket.event_count > 0);
	const labels = buckets.length
		? [
				chartLabel(buckets[0].bucket_start),
				chartLabel(buckets[Math.floor(buckets.length / 2)].bucket_start),
				chartLabel(buckets[buckets.length - 1].bucket_start),
			]
		: [];
	return {
		heading: 'Recent activity',
		ariaLabel: 'Recent activity trace',
		labels,
		traces: hasActivity
			? [
					buildTrace(
						buckets.map((bucket) => bucket.safe_count),
						'#667A68',
					),
					buildTrace(
						buckets.map((bucket) => bucket.caution_count),
						'#A87528',
					),
					buildTrace(
						buckets.map((bucket) => bucket.lockout_count),
						'#984A43',
					),
				]
			: [],
	};
}

function eventResult(outcome: AuthEventListItem['outcome']) {
	return {
		success: 'Success',
		failure: 'Failed',
		challenge: 'Challenge',
		logout: 'Signed out',
		unknown: 'Unknown',
	}[outcome];
}

function mapRecentActivity(data: OverviewData): OverviewActivityItem[] {
	return data.events.items.map((event) => {
		const band = event.risk_score?.score_band;
		return {
			id: event.id,
			time: formatTimestamp(event.occurred_at),
			initials: event.user_hash.slice(0, 2).toUpperCase(),
			user: `User ${event.user_hash.slice(0, 8)}`,
			login: displayLabel(event.auth_method ?? event.event_type),
			result: eventResult(event.outcome),
			risk: band ? displayLabel(band) : 'Not scored',
			score: event.risk_score
				? event.risk_score.fused_anomaly_score.toFixed(2)
				: '-',
			tone: band ?? 'neutral',
		};
	});
}

function mapReviewItems(data: OverviewData) {
	const analysis = data.pipelineHealth.components.find(
		(item) => item.component === 'analysis',
	);
	return [
		{
			id: '01',
			label: 'Caution sign-in decisions',
			value: String(data.cautionDecisions.pagination.total_count),
		},
		{
			id: '02',
			label: 'Lockout decisions',
			value: String(data.lockoutDecisions.pagination.total_count),
		},
		{
			id: '03',
			label: 'Analysis still in progress',
			value: String(analysis?.pending_count ?? 0),
		},
		{
			id: '04',
			label: 'Responses skipped in Simulation',
			value: String(data.skippedActions.pagination.total_count),
		},
	];
}

function decisionLabel(decision: PolicyDecision) {
	return `${displayLabel(decision.decision_band)} decision recorded`;
}

function actionLabel(action: EnforcementAction) {
	return `Response ${displayLabel(action.action_type)}`;
}

function mapSystemActivity(data: OverviewData): OverviewSystemActivityItem[] {
	const entries = [
		...data.events.items.map((event) => ({
			id: `event-${event.id}`,
			icon: LuDownload,
			label: 'Sign-in received',
			dateTime: event.occurred_at,
			meta: displayLabel(event.auth_method ?? event.event_type),
		})),
		...data.decisions.items.map((decision) => ({
			id: `decision-${decision.id}`,
			icon: LuSearch,
			label: decisionLabel(decision),
			dateTime: decision.decided_at,
			meta: displayLabel(decision.final_action),
		})),
		...data.alerts.items.map((alert: Alert) => ({
			id: `alert-${alert.id}`,
			icon: LuShieldCheck,
			label: 'Alert recorded',
			dateTime: alert.created_at,
			meta: `${displayLabel(alert.severity)} severity`,
		})),
		...data.actions.items.map((action: EnforcementAction) => ({
			id: `action-${action.id}`,
			icon: LuShieldCheck,
			label: actionLabel(action),
			dateTime: action.completed_at ?? action.requested_at,
			meta: `${displayLabel(action.status)} · ${displayLabel(action.integration_name)}`,
		})),
	];
	return entries
		.sort((left, right) => right.dateTime.localeCompare(left.dateTime))
		.slice(0, 4)
		.map(({ dateTime, ...entry }) => ({
			...entry,
			time: formatTimestamp(dateTime),
		}));
}

function mapMainSignal(data: OverviewData) {
	const cautionCount = data.cautionDecisions.pagination.total_count;
	const lockoutCount = data.lockoutDecisions.pagination.total_count;
	if (cautionCount > 0) return 'Caution decisions are the current review focus';
	if (lockoutCount > 0) return 'Lockout decisions need attention';
	return 'No risk decisions need review';
}

export function mapOverviewData(data: OverviewData): OverviewView {
	const eventCount = data.events.pagination.total_count;
	const reviewCount =
		data.cautionDecisions.pagination.total_count +
		data.lockoutDecisions.pagination.total_count;
	return {
		insight: eventCount
			? `${eventCount} recent sign-in${eventCount === 1 ? '' : 's'} recorded.`
			: 'No recent sign-in activity.',
		insightDetail: `${reviewCount} decision${reviewCount === 1 ? '' : 's'} need review.`,
		platformItems: mapPlatformItems(data),
		riskSegments: mapRiskSegments(data),
		chart: mapChart(data),
		recentActivity: mapRecentActivity(data),
		reviewItems: mapReviewItems(data),
		systemActivity: mapSystemActivity(data),
		mainSignal: mapMainSignal(data),
	};
}

export function createOverviewLoadingItems(): OverviewPlatformItem[] {
	return PLATFORM_CONFIG.map(({ icon, label }) => ({
		icon,
		label,
		status: '-',
		updated: '-',
		tone: 'neutral',
	}));
}
