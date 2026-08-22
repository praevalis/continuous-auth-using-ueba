import ProviderConnectionActions from './ProviderConnectionActions';
import ProviderConnectionDetails from './ProviderConnectionDetails';
import ProviderStatusBadge from './ProviderStatusBadge';
import { SiKeycloak } from 'react-icons/si';
import type { ProviderConnectionView } from './types';

export default function ProviderConnectionSection({
	connection,
	onTest,
	onEdit,
	onToggle,
}: {
	connection: ProviderConnectionView;
	onTest: () => void;
	onEdit: () => void;
	onToggle: () => void;
}) {
	const accent = connection.status === 'test_failed' ? 'bg-lockout' : 'bg-safe';
	return (
		<section className="border-b border-stone-300 py-8 last:border-b-0 lg:grid lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.7fr)] lg:gap-10">
			<div className="relative">
				<div className="flex items-start gap-3">
					<div className="flex min-w-0 items-center gap-3 max-[375px]:w-full">
						<div
							className="grid size-16 shrink-0 place-items-center rounded-panel border border-stone-300 text-primary"
							aria-hidden="true"
						>
							<SiKeycloak size={31} />
						</div>
						<div className="min-w-0">
							<h2 className="text-xl font-semibold tracking-[-0.02em] text-primary max-[375px]:text-base">
								{connection.connection_name}
							</h2>
							<p className="mt-2 text-sm text-carbon-300 max-[375px]:text-xs">
								Identity provider
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
							compact
						/>
					</div>
				</div>
			</div>
			<div className="mt-6 rounded-panel bg-stone-100/70 p-5 sm:mt-8 sm:p-6 lg:mt-0 lg:rounded-none lg:border-l lg:border-stone-300 lg:bg-transparent lg:p-0 lg:pl-10 lg:grid lg:grid-cols-[minmax(0,1fr)_auto] lg:items-start lg:gap-x-8">
				<ProviderConnectionDetails connection={connection} />
				<div className="hidden lg:col-start-2 lg:row-start-1 lg:block">
					<ProviderConnectionActions
						status={connection.status}
						onTest={onTest}
						onEdit={onEdit}
						onToggle={onToggle}
					/>
				</div>
			</div>
		</section>
	);
}
