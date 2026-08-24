import { useNavigate } from 'react-router-dom';
import type { OverviewActivityItem } from './types';

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
								className="grid min-h-12 grid-cols-[auto_1fr_auto] items-center gap-x-3 py-3 sm:grid-cols-[72px_minmax(130px,1.3fr)_minmax(90px,1fr)_70px_90px_60px]"
								key={index}
							>
								<span className="h-3 w-14 animate-pulse rounded bg-stone-200" />
								<span className="h-4 w-32 animate-pulse rounded bg-stone-200" />
								<span className="h-3 w-10 animate-pulse rounded bg-stone-200" />
							</div>
						))
					: items.map((item) => (
							<button
								type="button"
								className="grid min-h-12 w-full grid-cols-[auto_1fr_auto] items-center gap-x-3 gap-y-1 py-3 text-left transition hover:bg-stone-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary sm:grid-cols-[72px_minmax(130px,1.3fr)_minmax(90px,1fr)_70px_90px_60px]"
								onClick={() => navigate('/threat-feed')}
								aria-label={`Open threat feed for ${item.user}`}
								key={item.id}
							>
								<span className="font-mono text-xs text-carbon-700">
									{item.time}
								</span>
								<span className="flex min-w-0 items-center gap-2">
									<span className="grid size-6 shrink-0 place-items-center rounded-full bg-stone-100 text-[10px]">
										{item.initials}
									</span>
									<span className="truncate">{item.user}</span>
								</span>
								<span className="hidden sm:block">{item.login}</span>
								<span
									className={
										item.result === 'Failed' ? 'text-lockout' : 'text-safe'
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
								<span className="font-mono text-xs">{item.score} &nbsp;›</span>
							</button>
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
