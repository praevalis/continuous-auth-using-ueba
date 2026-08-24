import StatusBadge from '@/components/ui/StatusBadge';
import { LuCheck, LuCircleAlert } from 'react-icons/lu';
import type { components } from '@/api/generated/types';

const statusContent = {
	active: { label: 'Active', color: 'safe' },
	disabled: { label: 'Disabled', color: 'neutral' },
	test_failed: { label: 'Test failed', color: 'lockout' },
} as const;

export default function ProviderStatusBadge({
	status,
}: {
	status: components['schemas']['TenantProviderConnectionSchema']['status'];
}) {
	const content = statusContent[status];
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
		<StatusBadge
			tone={content.color}
			variant="outline"
			className="gap-2 px-3 py-1.5 text-sm"
			leading={icon}
		>
			{content.label}
		</StatusBadge>
	);
}
