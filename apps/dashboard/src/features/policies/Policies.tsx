import { useState } from 'react';
import PageLayout from '@/components/layout/PageLayout';
import { mockPolicies } from './mock-data';
import PolicyModeSelector from './PolicyModeSelector';
import PoliciesIntro from './PoliciesIntro';
import PolicyResponses from './PolicyResponses';
import PolicySelector from './PolicySelector';
import type { PolicyMode } from './types';

export default function Policies() {
	const [selectedPolicyId, setSelectedPolicyId] = useState(mockPolicies[0].id);
	const selectedPolicy =
		mockPolicies.find((policy) => policy.id === selectedPolicyId) ??
		mockPolicies[0];
	const [mode, setMode] = useState<PolicyMode>(selectedPolicy.mode);

	function handleCreatePolicy() {
		// The create workflow will be connected once policy configuration endpoints exist.
	}

	function handlePolicySelect(policyId: string) {
		const nextPolicy = mockPolicies.find((policy) => policy.id === policyId);
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
				policies={mockPolicies}
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
			<PolicyModeSelector value={mode} onChange={setMode} />
		</PageLayout>
	);
}
