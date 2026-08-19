import type { components } from '@/api/generated/types';

export type ActivityKind = 'analysis' | 'decisions' | 'response';
export type ActivityTone = 'safe' | 'caution' | 'lockout' | 'neutral';
export type ActivityApiStatus =
	| components['schemas']['AlertStatus']
	| components['schemas']['EnforcementActionStatus'];
export type ActivityDisplayStatus =
	| 'Succeeded'
	| 'Running'
	| 'Recorded'
	| 'Open'
	| 'Acknowledged'
	| 'Resolved'
	| 'Skipped'
	| 'Pending'
	| 'Sent'
	| 'Failed';

export type ActivityEntry = {
	id: string;
	time: string;
	title: string;
	user: string;
	status: ActivityDisplayStatus;
	statusTone: ActivityTone;
};

export type ActivitySection = {
	id: ActivityKind;
	title: string;
	statItems: Array<{ value: string; label: string; tone: ActivityTone }>;
	entries: ActivityEntry[];
};
