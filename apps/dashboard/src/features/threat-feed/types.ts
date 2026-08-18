export type RiskTone = 'safe' | 'caution' | 'lockout';

export type ThreatEvent = {
	id: string;
	time: string;
	initials: string;
	user: string;
	signInType: string;
	result: 'Success' | 'Failed' | 'Challenge';
	risk: 'Safe' | 'Caution' | 'Lockout';
	tone: RiskTone;
	score: number;
	response: string;
	device: string;
	network: string;
	observedSignals: Array<{
		label: string;
		observed: string;
		baseline: string;
	}>;
	responseActivity: Array<{ time: string; label: string; detail?: string }>;
};

export type ThreatFeedFilters = {
	search: string;
	result: string;
	risk: string;
};
