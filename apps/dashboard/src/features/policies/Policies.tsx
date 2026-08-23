import { useCallback, useEffect, useState } from 'react';
import { api } from '@/api/client';
import { useTenant } from '@/api/tenant';
import PageLayout from '@/components/layout/PageLayout';
import PolicyModeSelector from './PolicyModeSelector';
import PoliciesIntro from './PoliciesIntro';
import PolicyResponses from './PolicyResponses';
import PolicySelector from './PolicySelector';
import type { Policy, PolicyMode } from './types';

export default function Policies() {
	const { tenant } = useTenant();
	const [policies, setPolicies] = useState<Policy[]>([]);
	const [selectedPolicyId, setSelectedPolicyId] = useState('');
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [mode, setMode] = useState<PolicyMode>('shadow');
	const load = useCallback(async () => {
		if (!tenant) return;
		setLoading(true);
		try {
			const [profiles, modes] = await Promise.all([
				api.listProfiles(tenant.id),
				api.listModes(tenant.id),
			]);
			const mode = modes.find((item) => item.is_active)?.mode ?? 'shadow';
			setMode(mode);
			setPolicies(
				profiles.map((profile) => ({
					id: profile.id,
					name: profile.name,
					status: profile.is_active ? 'active' : 'inactive',
					description:
						profile.description ?? 'Risk thresholds for sign-in review.',
					mode,
					responses: [
						{
							band: 'safe',
							label: 'Safe',
							action: 'Allow sign-in',
							description: 'No response is taken.',
						},
						{
							band: 'caution',
							label: 'Caution',
							action: 'Ask for extra verification',
							description: `Review threshold ${profile.caution_threshold.toFixed(3)}.`,
						},
						{
							band: 'lockout',
							label: 'Lockout',
							action: 'End session',
							description: `Block threshold ${profile.lockout_threshold.toFixed(3)}.`,
						},
					],
				})),
			);
			setSelectedPolicyId((current) => current || profiles[0]?.id || '');
			setError(null);
		} catch (reason) {
			setError(
				reason instanceof Error
					? reason.message
					: 'Unable to load risk settings',
			);
		} finally {
			setLoading(false);
		}
	}, [tenant]);
	useEffect(() => {
		queueMicrotask(() => void load());
	}, [load]);
	const selectedPolicy =
		policies.find((policy) => policy.id === selectedPolicyId) ?? policies[0];
	if (loading)
		return (
			<PageLayout title="Policies">
				<p className="mt-10 text-sm text-carbon-500">Loading risk settings…</p>
			</PageLayout>
		);
	if (error || !selectedPolicy)
		return (
			<PageLayout title="Policies">
				<p className="mt-10 text-sm text-lockout">
					{error ?? 'No risk profiles are configured.'}
				</p>
				<button
					className="mt-4 rounded-control border border-primary px-4 py-2 text-sm"
					onClick={() => void load()}
				>
					Retry
				</button>
			</PageLayout>
		);

	function handleCreatePolicy() {
		void load();
	}

	function handlePolicySelect(policyId: string) {
		const nextPolicy = policies.find((policy) => policy.id === policyId);
		if (!nextPolicy) return;
		setSelectedPolicyId(nextPolicy.id);
		setMode(nextPolicy.mode);
	}

	function handleEditResponse() {
		// The edit workflow will be connected once policy configuration endpoints exist.
	}

	return (
		<PageLayout title="Policies">
			<PoliciesIntro onCreatePolicy={handleCreatePolicy} />
			<PolicySelector
				policies={policies}
				selectedPolicy={selectedPolicy}
				onSelect={handlePolicySelect}
			/>
			<div className="mt-6 border-b border-stone-300" />
			<section className="mt-8" aria-labelledby="selected-policy-heading">
				<div className="flex items-start justify-between gap-4">
					<div className="w-full">
						<div className="flex items-center justify-between gap-4 lg:block">
							<h2
								id="selected-policy-heading"
								className="text-xl font-semibold tracking-[-0.03em] text-primary sm:text-2xl"
							>
								{selectedPolicy.name}
							</h2>
							<button
								type="button"
								className="inline-flex min-h-10 shrink-0 items-center rounded-control border border-primary px-3 py-2 text-sm text-primary transition hover:bg-primary-soft lg:hidden"
								onClick={handleCreatePolicy}
							>
								Create policy
							</button>
						</div>
						<p className="mt-2 text-sm text-carbon-300 sm:text-base">
							{selectedPolicy.description}
						</p>
					</div>
				</div>
			</section>
			<PolicyResponses
				responses={selectedPolicy.responses}
				onEdit={handleEditResponse}
			/>
			<PolicyModeSelector
				value={mode}
				onChange={(nextMode) => {
					setMode(nextMode);
					void api
						.createMode(tenant!.id, {
							mode: nextMode,
							effective_from: new Date().toISOString(),
						})
						.then(load);
				}}
			/>
		</PageLayout>
	);
}
