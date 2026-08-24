import { LuBan, LuPencil, LuPower, LuRefreshCw } from 'react-icons/lu';
import IconButton from '@/components/ui/IconButton';
import Button from '@/components/ui/Button';
import type { components } from '@/api/generated/types';

export default function ProviderConnectionActions({
	status,
	onTest,
	onEdit,
	onToggle,
	compact = false,
	busy = false,
}: {
	status: components['schemas']['TenantProviderConnectionSchema']['status'];
	onTest: () => void;
	onEdit: () => void;
	onToggle: () => void;
	compact?: boolean;
	busy?: boolean;
}) {
	const active = status === 'active';
	const connectionDisabled = status === 'disabled';
	if (compact) {
		return (
			<div className="flex items-center gap-1">
				<IconButton
					icon={<LuRefreshCw className="text-safe" size={19} />}
					label="Test connection"
					onClick={onTest}
					disabled={busy || connectionDisabled}
					className="text-primary transition hover:bg-primary-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
				/>
				<IconButton
					icon={<LuPencil className="text-caution" size={19} />}
					label="Edit provider"
					onClick={onEdit}
					disabled={busy || connectionDisabled}
					className="text-primary transition hover:bg-primary-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
				/>
				<IconButton
					icon={
						active ? (
							<LuBan className="text-lockout" size={19} />
						) : (
							<LuPower className="text-safe" size={19} />
						)
					}
					label={active ? 'Disable provider' : 'Activate provider'}
					onClick={onToggle}
					disabled={busy}
					className="text-primary transition hover:bg-primary-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
				/>
			</div>
		);
	}
	return (
		<div className={`flex items-center ${compact ? 'gap-1' : 'gap-3'}`}>
			<Button
				onClick={onTest}
				disabled={busy || connectionDisabled}
				size="sm"
				leading={<LuRefreshCw className="text-safe" size={15} />}
				className="gap-1.5 border-stone-300 px-3 py-1.5 text-xs"
			>
				Test
			</Button>
			<Button
				onClick={onEdit}
				disabled={busy || connectionDisabled}
				size="sm"
				leading={<LuPencil className="text-caution" size={15} />}
				className="gap-1.5 border-stone-300 px-3 py-1.5 text-xs"
			>
				Edit
			</Button>
			<Button
				onClick={onToggle}
				disabled={busy}
				size="sm"
				leading={
					active ? (
						<LuBan className="text-lockout" size={15} />
					) : (
						<LuPower className="text-safe" size={15} />
					)
				}
				className="gap-1.5 border-stone-300 px-3 py-1.5 text-xs"
			>
				{active ? 'Disable' : 'Activate'}
			</Button>
		</div>
	);
}
