type OverviewIntroProps = {
	heading: string;
	description: string;
	insight: string;
	insightDetail: string;
};

export default function OverviewIntro({
	heading,
	description,
	insight,
	insightDetail,
}: OverviewIntroProps) {
	return (
		<section className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
			<div>
				<h1 className="max-w-4xl text-3xl font-semibold leading-tight tracking-[-0.035em] text-primary sm:text-4xl">
					{heading}
				</h1>
				<p className="mt-3 text-base text-carbon-300">{description}</p>
			</div>
			<p className="border-l-2 border-primary pl-4 text-base leading-6 text-carbon-700 lg:mt-1 lg:max-w-xs">
				{insight}
				<br />
				{insightDetail}
			</p>
		</section>
	);
}
