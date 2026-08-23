import { useMemo, useState } from 'react';
import { useTenant } from '@/api/tenant';
import PageLayout from '@/components/layout/PageLayout';
import Slider from '@/components/ui/Slider';
import {
	usePolicies,
	usePolicyModeMutation,
	useThresholdProfileMutation,
} from '@/hooks';
import PolicyModeSelector, { PolicyModeSkeleton } from './PolicyModeSelector';
import PoliciesIntro from './PoliciesIntro';
import PolicyResponses, { PolicyResponsesSkeleton } from './PolicyResponses';
import PolicySelector, {
	PolicySelectorEmpty,
	PolicySelectorSkeleton,
} from './PolicySelector';
import CreateThresholdProfileDialog from './CreateThresholdProfileDialog';
import { mapThresholdProfile } from './adapters';
import type { ThresholdProfileCreate } from '@/api/contracts';
import type { Policy, PolicyMode } from './types';

export default function Policies() {
	const { tenant } = useTenant();
	const [selectedPolicyId, setSelectedPolicyId] = useState('');
	const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
	const policyResource = usePolicies(tenant?.id);
	const modeMutation = usePolicyModeMutation(tenant?.id);
	const profileMutation = useThresholdProfileMutation(tenant?.id);
	const mode: PolicyMode = policyResource.data?.mode ?? 'shadow';
	const policies = useMemo<Policy[]>(
		() =>
			policyResource.data?.profiles.map((profile) =>
				mapThresholdProfile(profile, mode),
			) ?? [],
		[mode, policyResource.data],
	);
	const loading = policyResource.loading;
	const error = policyResource.error;
	const selectedPolicy =
		policies.find((policy) => policy.id === selectedPolicyId) ??
		policies.find((policy) => policy.status === 'active') ??
		policies[0];
	const unavailableMessage =
		error?.message ?? 'No risk profiles are configured.';

	function handleCreatePolicy() {
		setIsCreateDialogOpen(true);
	}

	async function handleCreateProfile(profile: ThresholdProfileCreate) {
		const createdProfile = await profileMutation.mutateAsync(profile);
		setSelectedPolicyId(createdProfile.id);
		setIsCreateDialogOpen(false);
		await policyResource.refresh();
	}

	function handlePolicySelect(policyId: string) {
		const nextPolicy = policies.find((policy) => policy.id === policyId);
		if (!nextPolicy) return;
		setSelectedPolicyId(nextPolicy.id);
	}

	async function handleModeChange(nextMode: PolicyMode) {
		if (!tenant || modeMutation.pending) return;
		try {
			await modeMutation.mutateAsync({
				mode: nextMode,
				effective_from: new Date().toISOString(),
			});
			await policyResource.refresh();
		} catch {
			// The mutation error is rendered by the mode selector.
		}
	}

	return (
		<PageLayout title="Policies">
			<PoliciesIntro onCreatePolicy={handleCreatePolicy} />
			{loading ? (
				<PolicySelectorSkeleton />
			) : !error && selectedPolicy ? (
				<PolicySelector
					policies={policies}
					selectedPolicy={selectedPolicy}
					onSelect={handlePolicySelect}
				/>
			) : (
				<PolicySelectorEmpty
					onRetry={error ? () => void policyResource.refresh() : undefined}
				/>
			)}
			<div className="mt-6 border-b border-stone-300" />
			<section className="mt-8" aria-labelledby="selected-policy-heading">
				<div className="flex items-start justify-between gap-4">
					<div className="w-full">
						{loading ? (
							<>
								<div
									className="h-8 w-56 animate-pulse rounded bg-stone-200"
									aria-hidden="true"
								/>
								<div
									className="mt-3 h-5 w-80 max-w-full animate-pulse rounded bg-stone-200"
									aria-hidden="true"
								/>
								<div
									className="mt-4 h-4 w-28 animate-pulse rounded bg-stone-200"
									aria-hidden="true"
								/>
								<div
									className="mt-2 h-5 w-80 max-w-full animate-pulse rounded bg-stone-200"
									aria-hidden="true"
								/>
							</>
						) : !error && selectedPolicy ? (
							<>
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
								<div className="mt-4 max-w-sm">
									<div className="flex items-center justify-between gap-3">
										<span className="text-sm text-carbon-300">
											Fusion alpha
										</span>
										{selectedPolicy.fusionAlpha === null ? (
											<span className="rounded-control border border-stone-300 px-2 py-1 text-xs text-carbon-500">
												Model default
											</span>
										) : (
											<span className="font-mono text-xs text-carbon-700">
												{selectedPolicy.fusionAlpha.toFixed(2)}
											</span>
										)}
									</div>
									{selectedPolicy.fusionAlpha !== null && (
										<>
											<Slider
												ariaLabel="Fusion alpha"
												value={selectedPolicy.fusionAlpha}
												onChange={() => undefined}
												disabled
												variant="soft-carbon"
											/>
										</>
									)}
								</div>
							</>
						) : (
							<p className="text-sm text-lockout" role="alert">
								{unavailableMessage}
							</p>
						)}
					</div>
				</div>
			</section>
			{loading ? (
				<PolicyResponsesSkeleton />
			) : !error && selectedPolicy ? (
				<PolicyResponses responses={selectedPolicy.responses} />
			) : null}
			{loading ? (
				<PolicyModeSkeleton />
			) : !error ? (
				<PolicyModeSelector
					value={mode}
					onChange={(nextMode) => void handleModeChange(nextMode)}
					error={modeMutation.error}
					pending={modeMutation.pending}
				/>
			) : (
				<section
					className="mt-10 border-t border-stone-300 pt-6"
					aria-label="Policy mode"
				>
					<h2 className="text-base font-medium text-primary">Mode</h2>
				</section>
			)}
			{isCreateDialogOpen && (
				<CreateThresholdProfileDialog
					onClose={() => setIsCreateDialogOpen(false)}
					onCreate={handleCreateProfile}
					pending={profileMutation.pending}
					error={profileMutation.error}
				/>
			)}
		</PageLayout>
	);
}
