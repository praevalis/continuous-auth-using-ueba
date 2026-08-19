export type PolicyMode = 'shadow' | 'alert_only' | 'enforce';

export type PolicyRisk = 'safe' | 'caution' | 'lockout';

export type PolicyResponse = {
	band: PolicyRisk;
	label: string;
	action: string;
	description: string;
};

export type Policy = {
	id: string;
	name: string;
	status: 'active' | 'inactive';
	description: string;
	mode: PolicyMode;
	responses: PolicyResponse[];
};
