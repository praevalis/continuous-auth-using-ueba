import Badge from '@/components/ui/Badge';
import { LuCheck, LuCircleAlert } from 'react-icons/lu';
import type { TenantProviderConnection } from './types';

const statusContent = {
	active: { label: 'Active', color: 'safe' },
	disabled: { label: 'Disabled', color: 'neutral' },
	test_failed: { label: 'Test failed', color: 'lockout' },
} as const;

export default function ProviderStatusBadge({
	status,
}: {
	status: TenantProviderConnection['status'];
}) {
	const content = statusContent[status];
	const colorClasses = {
		safe: 'border-safe/60 bg-paper-50 text-safe',
		neutral: 'border-neutral/60 bg-paper-50 text-neutral',
		lockout: 'border-lockout/60 bg-paper-50 text-lockout',
	}[content.color];
	const icon =
		content.color === 'safe' ? (
			<span className="grid size-4 shrink-0 place-items-center rounded-full border border-current text-current">
				<LuCheck size={10} />
			</span>
		) : content.color === 'lockout' ? (
			<LuCircleAlert className="size-4 shrink-0" />
		) : (
			<span className="size-2 shrink-0 rounded-full bg-current" />
		);
	return (
		<Badge
			className={`rounded-control gap-2 border px-3 py-1.5 text-sm font-normal ${colorClasses}`}
			leading={icon}
		>
			{content.label}
		</Badge>
	);
}
