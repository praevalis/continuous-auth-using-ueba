import {
	LuActivity,
	LuClock3,
	LuLockKeyhole,
	LuShieldAlert,
} from 'react-icons/lu';
import Badge from '@/components/ui/Badge';

const signals = [
	{
		value: '23',
		label: 'lockout signals',
		icon: LuLockKeyhole,
		tone: 'text-lockout',
	},
	{
		value: '87',
		label: 'caution signals',
		icon: LuShieldAlert,
		tone: 'text-caution',
	},
	{ value: '1,842', label: 'events', icon: LuActivity, tone: 'text-primary' },
];

export default function ThreatFeedSignals() {
	return (
		<section
			className="mt-8 border-y border-stone-300 py-4"
			aria-label="Threat feed signals"
		>
			<div className="grid grid-cols-2 gap-y-2 sm:grid-cols-4 sm:gap-y-0">
				{signals.map(({ value, label, icon: Icon, tone }, index) => (
					<div
						key={label}
						className={`flex items-center gap-2 px-2 sm:gap-3 sm:px-3 ${index % 2 === 1 ? 'border-l border-stone-300' : ''} ${index > 0 ? 'sm:border-l sm:border-stone-300' : ''} ${index >= 2 ? 'border-t border-stone-300 pt-3 sm:border-t-0 sm:pt-0' : ''}`}
					>
						<Icon className={tone} size={20} />
						<Badge>
							<span className="font-mono text-base text-primary sm:text-lg">
								{value}
							</span>
							<span className="text-xs text-carbon-300 sm:text-sm">
								{label}
							</span>
						</Badge>
					</div>
				))}
				<div className="relative flex items-center gap-2 border-t border-stone-300 px-2 pt-3 before:absolute before:left-0 before:top-1/2 before:h-6 before:-translate-y-1/2 before:border-l before:border-stone-300 before:content-[''] sm:gap-3 sm:border-l sm:border-t-0 sm:px-3 sm:pt-0 sm:before:hidden">
					<LuClock3 size={18} className="shrink-0" />
					<span className="text-xs text-carbon-300 sm:text-sm">
						Updated 12s ago
					</span>
				</div>
			</div>
		</section>
	);
}
