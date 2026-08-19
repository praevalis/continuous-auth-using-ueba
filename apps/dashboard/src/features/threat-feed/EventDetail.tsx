import { LuCheck, LuClock3, LuInfo } from 'react-icons/lu';
import Badge from '@/components/ui/Badge';
import SegmentedBar from '@/components/ui/SegmentedBar';
import type { ThreatEvent } from './types';

export default function EventDetail({
	event,
	mobile = false,
}: {
	event: ThreatEvent;
	mobile?: boolean;
}) {
	return (
		<aside
			className={
				mobile
					? 'border-t border-stone-300 bg-stone-100/70 p-4'
					: 'hidden border-l border-stone-300 pl-6 lg:block'
			}
			aria-labelledby={
				mobile ? 'event-detail-heading-mobile' : 'event-detail-heading-desktop'
			}
		>
			<div className="flex flex-col gap-1">
				<h2
					id={
						mobile
							? 'event-detail-heading-mobile'
							: 'event-detail-heading-desktop'
					}
					className="text-lg font-semibold text-primary"
				>
					Event detail
				</h2>
				<span className="hidden text-xs text-carbon-300 lg:block">
					Selected sign-in event
				</span>
			</div>
			<div className="mt-2 flex items-center gap-2">
				<span className="grid size-7 shrink-0 place-items-center rounded-full bg-stone-100 text-xs">
					{event.initials}
				</span>
				<div className="min-w-0">
					<p className="truncate text-xs">{event.user}</p>
					<p className="truncate text-xs text-carbon-300">
						{event.device} · {event.network}
					</p>
				</div>
			</div>
			<p className="mt-4 flex items-center gap-2 border-b border-stone-300 pb-4 text-xs text-caution">
				<span className="grid size-4 shrink-0 place-items-center rounded-full border border-caution text-[10px] font-semibold">
					!
				</span>
				This sign-in has a caution-level risk score.
			</p>
			<section className="border-b border-stone-300 py-4">
				<div className="flex items-start justify-between gap-3">
					<div>
						<h3 className="text-lg font-semibold text-primary">Decision</h3>
						<p className="mt-1 text-xs text-carbon-300">{event.response}</p>
					</div>
					<Badge className="rounded-control bg-neutral-soft px-2 py-1 text-xs text-carbon-300">
						Simulation
					</Badge>
				</div>
				<p className="mt-2 flex items-center gap-2 text-xs text-carbon-300">
					<LuInfo size={14} /> Recorded only; no provider action taken.
				</p>
			</section>
			<section className="border-b border-stone-300 py-4">
				<h3 className="text-section-title">Score composition</h3>
				<div className="mt-4">
					<div className="flex justify-between text-xs">
						<span className="text-safe">Safe</span>
						<span className="text-lockout">Lockout</span>
					</div>
					<div className="relative mt-2">
						<SegmentedBar
							items={[
								{ label: 'Safe', value: '34.9%', className: 'bg-safe' },
								{ label: 'Caution', value: '11.4%', className: 'bg-caution' },
								{ label: 'Lockout', value: '53.7%', className: 'bg-lockout' },
							]}
						/>
						<span
							className="absolute -top-2.5 -translate-x-1/2 text-xs"
							style={{ left: `${event.score * 100}%` }}
						>
							▼
						</span>
					</div>
					<div className="relative mt-2 h-4 font-mono text-[0.625rem] text-carbon-300 lg:text-label">
						<span className="absolute left-0">0.000</span>
						<span
							className="absolute -translate-x-1/2"
							style={{ left: '34.9%' }}
						>
							0.349
						</span>
						<span
							className="absolute -translate-x-1/2"
							style={{ left: '46.3%' }}
						>
							0.463
						</span>
						<span className="absolute right-0">1.000</span>
					</div>
				</div>
			</section>
			<section className="border-b border-stone-300 py-4">
				<h3 className="text-section-title">Observed signals</h3>
				<div className="mt-3 hidden grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)] gap-x-3 gap-y-2 text-xs lg:grid">
					<span className="font-semibold text-carbon-300">Metric</span>
					<span className="font-semibold text-carbon-300">Observed</span>
					<span className="font-semibold text-carbon-300">
						Compared with baseline
					</span>
					{event.observedSignals.map((signal) => (
						<div
							className="col-span-3 grid grid-cols-3 gap-x-3 text-[0.6875rem]"
							key={signal.label}
						>
							<span>{signal.label}</span>
							<span>{signal.observed}</span>
							<span>{signal.baseline}</span>
						</div>
					))}
				</div>
				<div className="mt-3 space-y-3 text-xs lg:hidden">
					{event.observedSignals.map((signal) => (
						<div
							className="grid grid-cols-2 gap-3 text-[0.6875rem]"
							key={signal.label}
						>
							<div>
								<span className="block text-carbon-300">{signal.label}</span>
								<span className="mt-1 block">{signal.observed}</span>
							</div>
							<div>
								<span className="block text-carbon-300">
									Compared with baseline
								</span>
								<span className="mt-1 block">{signal.baseline}</span>
							</div>
						</div>
					))}
				</div>
			</section>
			<section className="py-4">
				<h3 className="text-section-title">Response activity</h3>
				<div className="mt-3 space-y-3">
					{event.responseActivity.map((activity) => (
						<div className="flex items-start gap-3 text-xs" key={activity.time}>
							<span className="mt-0.5 flex size-5 shrink-0 items-center justify-center text-primary">
								<LuClock3 size={15} />
							</span>
							<span className="font-mono leading-5 text-carbon-300">
								{activity.time}
							</span>
							<span className="leading-5">{activity.label}</span>
						</div>
					))}
				</div>
				<Badge
					className="mt-3 text-sm text-safe"
					leading={
						<span className="grid size-4 place-items-center rounded-full bg-safe text-white">
							<LuCheck size={10} />
						</span>
					}
				>
					Success
				</Badge>
			</section>
		</aside>
	);
}
