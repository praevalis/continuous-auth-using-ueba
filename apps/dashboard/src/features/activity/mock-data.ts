import type {
	ActivityDisplayStatus,
	ActivitySection,
	ActivityTone,
} from './types';

const analysisEntries = [
	[
		'09:20:17',
		'Risk score calculated',
		'j•••••@example.com',
		'Succeeded',
		'safe',
	],
	[
		'09:18:42',
		'Analysis still in progress',
		'r•••••@example.com',
		'Running',
		'neutral',
	],
	[
		'09:15:00',
		'Feature snapshot created',
		'a•••••@example.com',
		'Succeeded',
		'safe',
	],
	['09:12:33', 'Event normalized', 'j•••••@example.com', 'Succeeded', 'safe'],
	[
		'09:11:07',
		'Baseline comparison completed',
		'k•••••@example.com',
		'Succeeded',
		'safe',
	],
	[
		'09:09:44',
		'Processing retry queued',
		's•••••@example.com',
		'Running',
		'neutral',
	],
	[
		'09:07:18',
		'Risk features prepared',
		'm•••••@example.com',
		'Succeeded',
		'safe',
	],
	[
		'09:05:42',
		'User baseline refreshed',
		'd•••••@example.com',
		'Succeeded',
		'safe',
	],
	[
		'09:03:11',
		'Analysis retry scheduled',
		'p•••••@example.com',
		'Running',
		'neutral',
	],
	[
		'09:01:56',
		'Event enrichment completed',
		'c•••••@example.com',
		'Succeeded',
		'safe',
	],
	[
		'08:59:24',
		'Historical context loaded',
		'n•••••@example.com',
		'Succeeded',
		'safe',
	],
	[
		'08:57:08',
		'Feature preparation started',
		'v•••••@example.com',
		'Running',
		'neutral',
	],
] as const;

const decisionEntries = [
	[
		'09:20:17',
		'Caution decision recorded',
		'j•••••@example.com',
		'Recorded',
		'caution',
	],
	[
		'09:15:09',
		'Lockout decision recorded',
		'a•••••@example.com',
		'Recorded',
		'caution',
	],
	['09:14:03', 'Alert opened', 'j•••••@example.com', 'Open', 'caution'],
	[
		'09:12:08',
		'Safe decision recorded',
		'k•••••@example.com',
		'Recorded',
		'safe',
	],
	[
		'09:10:47',
		'Response skipped in Simulation',
		'r•••••@example.com',
		'Skipped',
		'caution',
	],
	[
		'09:08:22',
		'Decision reason updated',
		'a•••••@example.com',
		'Recorded',
		'caution',
	],
	[
		'09:06:17',
		'Caution decision reviewed',
		'm•••••@example.com',
		'Recorded',
		'caution',
	],
	[
		'09:04:49',
		'Alert acknowledged',
		'd•••••@example.com',
		'Acknowledged',
		'caution',
	],
	[
		'09:02:31',
		'Safe decision recorded',
		'p•••••@example.com',
		'Recorded',
		'safe',
	],
	['09:00:18', 'Lockout alert opened', 'c•••••@example.com', 'Open', 'lockout'],
	[
		'08:58:42',
		'Decision metadata stored',
		'n•••••@example.com',
		'Recorded',
		'caution',
	],
	[
		'08:56:23',
		'Simulation outcome recorded',
		'v•••••@example.com',
		'Skipped',
		'caution',
	],
] as const;

const responseEntries = [
	[
		'09:18:10',
		'Extra verification requested',
		'j•••••@example.com',
		'Succeeded',
		'safe',
	],
	['09:15:09', 'Lock account', 'a•••••@example.com', 'Skipped', 'caution'],
	['09:14:03', 'End session', 'k•••••@example.com', 'Failed', 'lockout'],
	[
		'09:12:57',
		'No provider action taken',
		'r•••••@example.com',
		'Succeeded',
		'safe',
	],
	[
		'09:11:36',
		'Alert notification sent',
		's•••••@example.com',
		'Succeeded',
		'safe',
	],
	[
		'09:09:28',
		'Provider retry queued',
		'a•••••@example.com',
		'Running',
		'neutral',
	],
	[
		'09:07:52',
		'Verification notification sent',
		'm•••••@example.com',
		'Succeeded',
		'safe',
	],
	[
		'09:05:20',
		'Session termination requested',
		'd•••••@example.com',
		'Succeeded',
		'safe',
	],
	[
		'09:03:44',
		'Provider action pending',
		'p•••••@example.com',
		'Pending',
		'neutral',
	],
	[
		'09:01:26',
		'Account lock requested',
		'c•••••@example.com',
		'Failed',
		'lockout',
	],
	[
		'08:59:10',
		'Response recorded in Simulation',
		'n•••••@example.com',
		'Skipped',
		'caution',
	],
	[
		'08:57:36',
		'Provider request accepted',
		'v•••••@example.com',
		'Succeeded',
		'safe',
	],
] as const;

function entriesFrom(
	entries: readonly (readonly [
		string,
		string,
		string,
		ActivityDisplayStatus,
		ActivityTone,
	])[],
	prefix: string,
) {
	return entries.map(([time, title, user, status, statusTone], index) => ({
		id: `${prefix}-${index + 1}`,
		time,
		title,
		user,
		status,
		statusTone,
	}));
}

export const mockActivitySections: ActivitySection[] = [
	{
		id: 'analysis',
		title: 'Analysis',
		statItems: [
			{ value: '18', label: 'completed', tone: 'safe' },
			{ value: '2', label: 'still running', tone: 'neutral' },
		],
		entries: entriesFrom(analysisEntries, 'analysis'),
	},
	{
		id: 'decisions',
		title: 'Decisions & alerts',
		statItems: [
			{ value: '12', label: 'decisions', tone: 'caution' },
			{ value: '4', label: 'alerts open', tone: 'caution' },
		],
		entries: entriesFrom(decisionEntries, 'decision'),
	},
	{
		id: 'response',
		title: 'Response execution',
		statItems: [
			{ value: '6', label: 'succeeded', tone: 'safe' },
			{ value: '1', label: 'skipped in Simulation', tone: 'caution' },
		],
		entries: entriesFrom(responseEntries, 'response'),
	},
];
