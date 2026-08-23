export type RiskTone = 'safe' | 'caution' | 'lockout' | 'unknown';

export type ThreatEvent = {
	id: string;
	dateTime: string;
	time: string;
	initials: string;
	user: string;
	signInType: string;
	result: 'Success' | 'Failed' | 'Challenge' | 'Signed out' | 'Unknown';
	risk: 'Safe' | 'Caution' | 'Lockout' | 'Unknown';
	tone: RiskTone;
	score: number | null;
	cautionThreshold: number | null;
	lockoutThreshold: number | null;
	response: string;
	decisionStatus: string;
	decisionNote: string;
	responseStatus: string;
	device: string;
	network: string;
	observedSignals: Array<{
		label: string;
		observed: string;
		baseline: string;
	}>;
	responseActivity: Array<{
		id: string;
		dateTime: string;
		time: string;
		label: string;
	}>;
};

export type ThreatFeedFilters = {
	search: string;
	result: string;
	risk: string;
};
