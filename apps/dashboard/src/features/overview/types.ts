import type { IconType } from 'react-icons';

export type OverviewTone = 'safe' | 'caution' | 'lockout' | 'neutral';

export type OverviewPlatformItem = {
	icon: IconType;
	label: string;
	status: string;
	updated: string;
	tone: OverviewTone;
};

export type OverviewRiskSegment = {
	label: string;
	value: string;
	className: string;
	tone: string;
};

export type OverviewActivityItem = {
	id: string;
	time: string;
	initials: string;
	user: string;
	login: string;
	result: string;
	risk: string;
	score: string;
	tone: OverviewTone;
};

export type OverviewReviewItem = {
	id: string;
	label: string;
	value: string;
};

export type OverviewActivityTrace = {
	path: string;
	color: string;
};

export type OverviewChart = {
	heading: string;
	traces: OverviewActivityTrace[];
	labels: string[];
	ariaLabel: string;
};

export type OverviewSystemActivityItem = {
	id: string;
	icon: IconType;
	label: string;
	time: string;
	meta: string;
};

export type OverviewView = {
	insight: string;
	insightDetail: string;
	platformItems: OverviewPlatformItem[];
	riskSegments: OverviewRiskSegment[];
	chart: OverviewChart;
	recentActivity: OverviewActivityItem[];
	reviewItems: OverviewReviewItem[];
	systemActivity: OverviewSystemActivityItem[];
	mainSignal: string;
};
