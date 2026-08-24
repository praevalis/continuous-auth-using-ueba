import type { OperatingModeValue } from '@/api/contracts';

export type PolicyMode = OperatingModeValue;

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
	fusionAlpha: number | null;
	mode: PolicyMode;
	responses: PolicyResponse[];
};
