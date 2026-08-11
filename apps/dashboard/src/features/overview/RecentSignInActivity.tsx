type ActivityItem = {
	time: string;
	initials: string;
	user: string;
	login: string;
	result: string;
	risk: string;
	score: string;
	tone: string;
};

export default function RecentSignInActivity({
	items,
}: {
	items: ActivityItem[];
}) {
	return (
		<section aria-labelledby="recent-heading">
			<h2 id="recent-heading" className="text-lg font-semibold">
				Recent sign-in activity
			</h2>
			<div className="mt-4 divide-y divide-stone-300/80 text-sm">
				{items.map((item) => (
					<div
						className="grid min-h-12 grid-cols-[auto_1fr_auto] items-center gap-x-3 gap-y-1 py-3 sm:grid-cols-[72px_minmax(130px,1.3fr)_minmax(90px,1fr)_70px_90px_60px]"
						key={item.time}
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
								className={`inline-block size-2.5 rounded-full ${item.tone === 'safe' ? 'bg-safe' : item.tone === 'caution' ? 'bg-caution' : 'bg-lockout'}`}
								aria-label={item.risk}
							/>
							{item.risk}
						</span>
						<span className="font-mono text-xs">{item.score} &nbsp;›</span>
					</div>
				))}
			</div>
		</section>
	);
}
