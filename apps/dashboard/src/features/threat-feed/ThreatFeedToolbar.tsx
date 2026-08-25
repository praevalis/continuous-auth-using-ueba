import { useEffect, useRef, useState } from 'react';
import { LuRefreshCw, LuSearch } from 'react-icons/lu';
import Dropdown from '@/components/ui/Dropdown';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import type { ThreatFeedTimeRange } from '@/hooks/useThreatFeed';

const resultOptions = [
	{ label: 'All results', value: 'all' },
	{ label: 'Success', value: 'success' },
	{ label: 'Failed', value: 'failed' },
];
const riskOptions = [
	{ label: 'All risk levels', value: 'all' },
	{ label: 'Safe', value: 'safe' },
	{ label: 'Caution', value: 'caution' },
	{ label: 'Lockout', value: 'lockout' },
];

function FilterControl({
	label,
	options,
	value,
	onChange,
}: {
	label: string;
	options: Array<{ label: string; value: string }>;
	value: string;
	onChange: (_value: string) => void;
}) {
	return (
		<div className="order-3 flex h-10 w-full items-center rounded-control border border-stone-300 bg-transparent text-xs lg:order-2">
			<Dropdown
				label={label}
				options={options}
				value={value}
				onChange={onChange}
				fullWidth
			/>
		</div>
	);
}

export default function ThreatFeedToolbar({
	search,
	onSearchChange,
	result,
	onResultChange,
	risk,
	onRiskChange,
	timeRange,
	onTimeRangeChange,
	onRefresh,
}: {
	search: string;
	onSearchChange: (_value: string) => void;
	result: string;
	onResultChange: (_value: string) => void;
	risk: string;
	onRiskChange: (_value: string) => void;
	timeRange: ThreatFeedTimeRange;
	onTimeRangeChange: (_value: string) => void;
	onRefresh: () => void;
}) {
	const [isRefreshing, setIsRefreshing] = useState(false);
	const refreshTimeoutRef = useRef<number | null>(null);

	useEffect(
		() => () => {
			if (refreshTimeoutRef.current !== null) {
				window.clearTimeout(refreshTimeoutRef.current);
			}
		},
		[],
	);

	function handleRefresh() {
		onRefresh();
		setIsRefreshing(true);
		if (refreshTimeoutRef.current !== null) {
			window.clearTimeout(refreshTimeoutRef.current);
		}
		refreshTimeoutRef.current = window.setTimeout(
			() => setIsRefreshing(false),
			500,
		);
	}

	return (
		<div
			className="mb-8 grid w-full max-w-full min-w-0 grid-cols-5 items-center gap-2 lg:grid-cols-[minmax(13rem,2fr)_minmax(9rem,1fr)_minmax(9rem,1fr)_minmax(9rem,1fr)_auto]"
			aria-label="Threat feed controls"
		>
			<label className="col-span-4 flex h-10 min-w-0 items-center gap-2 rounded-control border border-stone-300 bg-transparent px-3 text-xs lg:order-1 lg:col-span-1">
				<LuSearch size={15} className="shrink-0 text-carbon-300" />
				<span className="sr-only">Search users or event IDs</span>
				<Input
					className="h-auto min-w-0 flex-1 rounded-none border-0 bg-transparent px-0 text-xs focus:border-0 focus-visible:border-0"
					placeholder="Search users or event IDs"
					value={search}
					onChange={(event) => onSearchChange(event.target.value)}
				/>
			</label>
			<div className="order-3 col-span-5 grid grid-cols-3 gap-2 lg:order-none lg:contents">
				<FilterControl
					label="Last 24 hours"
					options={[
						{ label: 'Last 24 hours', value: '24h' },
						{ label: 'Last 7 days', value: '7d' },
						{ label: 'Last 30 days', value: '30d' },
					]}
					value={timeRange}
					onChange={onTimeRangeChange}
				/>
				<FilterControl
					label="All results"
					options={resultOptions}
					value={result}
					onChange={onResultChange}
				/>
				<FilterControl
					label="All risk levels"
					options={riskOptions}
					value={risk}
					onChange={onRiskChange}
				/>
			</div>
			<Button
				onClick={handleRefresh}
				variant="quiet"
				size="sm"
				leading={
					<LuRefreshCw
						size={15}
						className={`transition-transform duration-500 ${isRefreshing ? 'rotate-[360deg]' : ''}`}
					/>
				}
				className="order-2 col-span-1 h-10 px-3 text-xs text-carbon-700 lg:order-5 lg:col-span-1 lg:justify-start"
			>
				<span className="hidden lg:inline">Refresh feed</span>
			</Button>
		</div>
	);
}
