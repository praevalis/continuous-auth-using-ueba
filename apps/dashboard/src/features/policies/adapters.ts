import type { ThresholdProfile } from '@/api/contracts';
import type { Policy, PolicyMode, PolicyResponse, PolicyRisk } from './types';

const responseActions: Record<PolicyMode, Record<PolicyRisk, string>> = {
	shadow: {
		safe: 'No action taken',
		caution: 'No action taken',
		lockout: 'No action taken',
	},
	alert_only: {
		safe: 'Allow sign-in',
		caution: 'Create alert',
		lockout: 'Create alert',
	},
	enforce: {
		safe: 'Allow sign-in',
		caution: 'Ask for extra verification',
		lockout: 'End session',
	},
};

function createResponses(
	profile: ThresholdProfile,
	mode: PolicyMode,
): PolicyResponse[] {
	const cautionThreshold = profile.caution_threshold.toFixed(3);
	const lockoutThreshold = profile.lockout_threshold.toFixed(3);

	return [
		{
			band: 'safe',
			label: 'Safe',
			action: responseActions[mode].safe,
			description: `Below caution threshold ${cautionThreshold}.`,
		},
		{
			band: 'caution',
			label: 'Caution',
			action: responseActions[mode].caution,
			description: `From ${cautionThreshold} up to ${lockoutThreshold}.`,
		},
		{
			band: 'lockout',
			label: 'Lockout',
			action: responseActions[mode].lockout,
			description: `At or above lockout threshold ${lockoutThreshold}.`,
		},
	];
}

export function mapThresholdProfile(
	profile: ThresholdProfile,
	mode: PolicyMode,
): Policy {
	return {
		id: profile.id,
		name: profile.name,
		status: profile.is_active ? 'active' : 'inactive',
		description: profile.description ?? 'Risk thresholds for sign-in review.',
		fusionAlpha: profile.fusion_alpha ?? null,
		mode,
		responses: createResponses(profile, mode),
	};
}
