import StatusBadge from '@/components/ui/StatusBadge';

export default function ResourceStatusBadge({
	label,
	tone,
	className = '',
}: {
	label: string;
	tone: 'safe' | 'lockout';
	className?: string;
}) {
	return (
		<StatusBadge tone={tone} className={className}>
			{label}
		</StatusBadge>
	);
}
