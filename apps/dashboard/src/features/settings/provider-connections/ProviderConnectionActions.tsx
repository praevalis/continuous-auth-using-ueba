import { LuBan, LuPencil, LuPower, LuRefreshCw } from 'react-icons/lu';
import type { components } from '@/api/generated/types';

export default function ProviderConnectionActions({
	status,
	onTest,
	onEdit,
	onToggle,
	compact = false,
}: {
	status: components['schemas']['TenantProviderConnectionSchema']['status'];
	onTest: () => void;
	onEdit: () => void;
	onToggle: () => void;
	compact?: boolean;
}) {
	const active = status === 'active';
	const buttonClass = `inline-flex items-center justify-center rounded-control border border-stone-300 text-primary transition hover:bg-primary-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary ${compact ? 'size-10' : 'gap-1.5 px-3 py-1.5 text-xs'}`;
	return (
		<div className={`flex items-center ${compact ? 'gap-1' : 'gap-3'}`}>
			<button
				type="button"
				onClick={onTest}
				className={buttonClass}
				aria-label="Test connection"
				title="Test connection"
			>
				<LuRefreshCw className="text-safe" size={compact ? 19 : 15} />
				{!compact && 'Test'}
			</button>
			<button
				type="button"
				onClick={onEdit}
				className={buttonClass}
				aria-label="Edit provider"
				title="Edit provider"
			>
				<LuPencil className="text-caution" size={compact ? 19 : 15} />
				{!compact && 'Edit'}
			</button>
			<button
				type="button"
				onClick={onToggle}
				className={buttonClass}
				aria-label={active ? 'Disable provider' : 'Activate provider'}
				title={active ? 'Disable provider' : 'Activate provider'}
			>
				{active ? (
					<LuBan className="text-lockout" size={compact ? 19 : 15} />
				) : (
					<LuPower className="text-safe" size={compact ? 19 : 15} />
				)}
				{!compact && (active ? 'Disable' : 'Activate')}
			</button>
		</div>
	);
}
