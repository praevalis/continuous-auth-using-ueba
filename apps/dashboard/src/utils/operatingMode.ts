import type { OperatingModeValue } from '@/api/contracts';

export const operatingModeLabels: Record<OperatingModeValue, string> = {
	shadow: 'Simulation',
	alert_only: 'Notify only',
	enforce: 'Active response',
};

export const operatingModeOptions: Array<{
	value: OperatingModeValue;
	label: string;
}> = Object.entries(operatingModeLabels).map(([value, label]) => ({
	value: value as OperatingModeValue,
	label,
}));
