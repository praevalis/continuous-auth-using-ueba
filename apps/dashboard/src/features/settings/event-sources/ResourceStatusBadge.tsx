import Badge from '@/components/ui/Badge';

export default function ResourceStatusBadge({
	label,
	tone,
	className = '',
}: {
	label: string;
	tone: 'safe' | 'lockout';
	className?: string;
}) {
	const classes =
		tone === 'safe'
			? {
					badge: 'border-safe/40 bg-safe-soft text-safe',
					dot: 'bg-safe',
				}
			: {
					badge: 'border-lockout/40 bg-lockout-soft text-lockout',
					dot: 'bg-lockout',
				};
	return (
		<Badge
			className={`rounded-control border px-2 py-1 text-xs font-normal ${classes.badge} ${className}`}
			leading={
				<span
					className={`size-2 rounded-full ${classes.dot}`}
					aria-hidden="true"
				/>
			}
		>
			{label}
		</Badge>
	);
}
