import ProviderConnectionActions from './ProviderConnectionActions';
import ProviderConnectionDetails from './ProviderConnectionDetails';
import ProviderStatusBadge from './ProviderStatusBadge';
import { LuPlug } from 'react-icons/lu';
import { SiKeycloak } from 'react-icons/si';
import type { ProviderConnectionView } from './types';

export default function ProviderConnectionSection({
	connection,
	onTest,
	onEdit,
	onToggle,
	busy = false,
}: {
	connection: ProviderConnectionView;
	onTest: () => void;
	onEdit: () => void;
	onToggle: () => void;
	busy?: boolean;
}) {
	const accent = {
		active: 'bg-safe',
		disabled: 'bg-neutral',
		test_failed: 'bg-lockout',
	}[connection.status];
	const providerTypeLabel =
		connection.provider.provider_type === 'siem' ? 'SIEM' : 'Identity provider';
	return (
		<section className="border-b border-stone-300 py-8 last:border-b-0 lg:grid lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.7fr)] lg:gap-10">
			<div className="relative">
				<div className="flex items-start gap-3">
					<div className="flex min-w-0 items-center gap-3 max-[375px]:w-full">
						<div
							className="grid size-16 shrink-0 place-items-center rounded-panel border border-stone-300 text-primary"
							aria-hidden="true"
						>
							{connection.provider.provider_key === 'keycloak' ? (
								<SiKeycloak size={31} />
							) : (
								<LuPlug size={31} />
							)}
						</div>
						<div className="min-w-0">
							<h2 className="text-xl font-semibold tracking-[-0.02em] text-primary max-[375px]:text-base">
								{connection.connection_name}
							</h2>
							<p className="mt-2 text-sm text-carbon-300 max-[375px]:text-xs">
								{connection.provider.display_name} · {providerTypeLabel}
							</p>
						</div>
					</div>
				</div>
				<div className="relative mt-5 flex items-center justify-between gap-3 pl-3">
					<span
						className={`absolute inset-y-0 left-0 w-1 rounded-full ${accent}`}
						aria-hidden="true"
					/>
					<ProviderStatusBadge status={connection.status} />
					<div className="lg:hidden">
						<ProviderConnectionActions
							status={connection.status}
							onTest={onTest}
							onEdit={onEdit}
							onToggle={onToggle}
							busy={busy}
							compact
						/>
					</div>
				</div>
			</div>
			<div className="mt-6 rounded-panel bg-stone-100/70 p-5 sm:mt-8 sm:p-6 lg:mt-0 lg:grid lg:grid-cols-[minmax(0,1fr)_auto] lg:items-start lg:gap-x-8">
				<ProviderConnectionDetails connection={connection} />
				<div className="hidden lg:col-start-2 lg:row-start-1 lg:block">
					<ProviderConnectionActions
						status={connection.status}
						onTest={onTest}
						onEdit={onEdit}
						onToggle={onToggle}
						busy={busy}
					/>
				</div>
			</div>
		</section>
	);
}

export function ProviderConnectionSectionSkeleton() {
	return (
		<section className="border-b border-stone-300 py-8 last:border-b-0 lg:grid lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.7fr)] lg:gap-10">
			<div className="relative">
				<div className="flex items-center gap-3">
					<div className="size-16 animate-pulse rounded-panel bg-stone-200" />
					<div>
						<div className="h-6 w-48 animate-pulse rounded bg-stone-200" />
						<div className="mt-3 h-4 w-28 animate-pulse rounded bg-stone-200" />
					</div>
				</div>
				<div className="mt-5 h-6 w-24 animate-pulse rounded bg-stone-200" />
			</div>
			<div className="mt-6 rounded-panel bg-stone-100 p-5 sm:mt-8 sm:p-6 lg:mt-0">
				<div className="h-28 animate-pulse rounded bg-stone-200" />
			</div>
		</section>
	);
}
