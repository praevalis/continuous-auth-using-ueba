import { useEffect, useRef, useState } from 'react';
import { LuRefreshCw } from 'react-icons/lu';
import DateTimePicker from '@/components/ui/DateTimePicker';

export default function AuditControls({
	from,
	to,
	onFromChange,
	onToChange,
	onRefresh,
}: {
	from: string;
	to: string;
	onFromChange: (_value: string) => void;
	onToChange: (_value: string) => void;
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
		<section className="mt-12" aria-labelledby="audit-controls-heading">
			<h2
				id="audit-controls-heading"
				className="text-section-title text-primary"
			>
				Audit controls
			</h2>
			<div className="mt-4 grid w-full grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto] items-end gap-2 sm:gap-4 lg:w-fit lg:grid-cols-[14rem_14rem_auto]">
				<DateTimePicker label="From" value={from} onChange={onFromChange} />
				<DateTimePicker
					label="To"
					value={to}
					onChange={onToChange}
					align="end"
				/>
				<button
					type="button"
					onClick={handleRefresh}
					className="inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-control px-3 text-sm text-carbon-700 transition hover:bg-primary-soft"
				>
					<LuRefreshCw
						size={16}
						className={`transition-transform duration-500 ${isRefreshing ? 'rotate-[360deg]' : ''}`}
					/>
					<span className="hidden sm:inline">Refresh activity</span>
				</button>
			</div>
		</section>
	);
}
