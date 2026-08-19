import type { Policy } from './types';

export const mockPolicies: Policy[] = [
	{
		id: 'default-sign-in-policy',
		name: 'Default sign-in policy',
		status: 'active',
		description: 'Applies to all user sign-ins across the tenant.',
		mode: 'enforce',
		responses: [
			{
				band: 'safe',
				label: 'Safe',
				action: 'Allow sign-in',
				description:
					'Low risk. Sign-in is allowed with no additional action required.',
			},
			{
				band: 'caution',
				label: 'Caution',
				action: 'Ask for extra verification',
				description:
					'Moderate risk. Step-up verification is required to continue.',
			},
			{
				band: 'lockout',
				label: 'Lockout',
				action: 'Block sign-in',
				description: 'High risk. Sign-in is blocked and the account is locked.',
			},
		],
	},
];
