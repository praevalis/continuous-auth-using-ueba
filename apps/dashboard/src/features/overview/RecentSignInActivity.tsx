import { useNavigate } from 'react-router-dom';
import Button from '@/components/ui/Button';
import type { OverviewActivityItem } from './types';

function Timestamp({ value }: { value: string }) {
	const [date, time] = value.split(' · ');

	return (
		<span
			className="flex min-w-0 flex-col whitespace-nowrap font-mono text-xs leading-4 text-carbon-700"
			aria-label={value}
		>
			<span>{time ? `${date} ·` : date}</span>
			{time && <span>{time}</span>}
		</span>
	);
}

export default function RecentSignInActivity({
	items,
	loading = false,
}: {
	items: OverviewActivityItem[];
	loading?: boolean;
}) {
	const navigate = useNavigate();

	return (
		<section aria-labelledby="recent-heading">
			<h2 id="recent-heading" className="text-lg font-semibold">
				Recent sign-in activity
			</h2>
			<div className="mt-4 divide-y divide-stone-300/80 text-sm">
				{loading
					? Array.from({ length: 4 }, (_, index) => (
							<div
								className="grid min-h-12 grid-cols-[4rem_minmax(0,1fr)_4rem_4rem] items-center gap-x-2 gap-y-1 py-3 sm:grid-cols-[72px_minmax(130px,1.3fr)_minmax(90px,1fr)_70px_90px_60px]"
								key={index}
							>
								<span className="flex flex-col gap-1 sm:block">
									<span className="block h-3 w-14 animate-pulse rounded bg-stone-200" />
									<span className="block h-3 w-10 animate-pulse rounded bg-stone-200" />
								</span>
								<span className="h-4 w-32 animate-pulse rounded bg-stone-200" />
								<span className="h-3 w-10 animate-pulse rounded bg-stone-200" />
							</div>
						))
					: items.map((item) => (
							<Button
								variant="quiet"
								size="sm"
								className="grid min-h-12 w-full grid-cols-[4rem_minmax(0,1fr)_4rem_4rem] items-center justify-start gap-x-2 gap-y-1 rounded-none px-0 py-3 text-left text-sm hover:bg-stone-100 sm:grid-cols-[72px_minmax(130px,1.3fr)_minmax(90px,1fr)_70px_90px_60px]"
								onClick={() => navigate('/threat-feed')}
								aria-label={`Open threat feed for ${item.user}`}
								key={item.id}
							>
								<Timestamp value={item.time} />
								<span className="flex min-w-0 items-center gap-2 overflow-hidden">
									<span className="grid size-6 shrink-0 place-items-center rounded-full bg-stone-100 text-[10px]">
										{item.initials}
									</span>
									<span className="truncate">{item.user}</span>
								</span>
								<span className="hidden sm:block">{item.login}</span>
								<span
									className={
										item.result === 'Failed'
											? 'min-w-0 justify-self-start truncate whitespace-nowrap text-left text-lockout'
											: 'min-w-0 justify-self-start truncate whitespace-nowrap text-left text-safe'
									}
								>
									{item.result}
								</span>
								<span className="hidden items-center gap-2 sm:flex">
									<span
										className={`inline-block size-2.5 rounded-full ${item.tone === 'safe' ? 'bg-safe' : item.tone === 'caution' ? 'bg-caution' : item.tone === 'lockout' ? 'bg-lockout' : 'bg-carbon-300'}`}
										aria-label={item.risk}
									/>
									{item.risk}
								</span>
								<span className="min-w-0 truncate font-mono text-xs">
									{item.score} &nbsp;›
								</span>
							</Button>
						))}
				{!loading && items.length === 0 && (
					<p className="py-6 text-sm text-carbon-500">
						No recent sign-in activity.
					</p>
				)}
			</div>
		</section>
	);
}
