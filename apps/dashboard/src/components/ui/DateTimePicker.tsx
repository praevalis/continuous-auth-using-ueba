import { useEffect, useMemo, useRef, useState } from 'react';
import {
	LuCalendarDays,
	LuCheck,
	LuChevronLeft,
	LuChevronRight,
	LuMinus,
	LuPlus,
	LuX,
} from 'react-icons/lu';

type DateTimePickerProps = {
	label: string;
	value: string;
	onChange: (_value: string) => void;
	min?: string;
	max?: string;
	align?: 'start' | 'end';
};

const WEEKDAYS = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];

function parseDate(value: string) {
	const date = new Date(value);
	return Number.isNaN(date.getTime()) ? new Date() : date;
}

function toInputValue(date: Date) {
	const pad = (part: number) => String(part).padStart(2, '0');
	return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function getTimeParts(date: Date) {
	const hour = date.getHours();
	return {
		hour12: hour % 12 || 12,
		minute: date.getMinutes(),
		meridiem: hour >= 12 ? ('PM' as const) : ('AM' as const),
	};
}

function formatDateTime(value: string) {
	const date = parseDate(value);
	const today = new Date();
	const yesterday = new Date(today);
	yesterday.setDate(today.getDate() - 1);
	const isToday = date.toDateString() === today.toDateString();
	const isYesterday = date.toDateString() === yesterday.toDateString();
	const prefix = isToday
		? 'Today'
		: isYesterday
			? 'Yesterday'
			: date.toLocaleDateString(undefined, {
					month: 'short',
					day: 'numeric',
					year: 'numeric',
				});
	const time = date.toLocaleTimeString(undefined, {
		hour: '2-digit',
		minute: '2-digit',
		hour12: false,
	});

	return `${prefix}, ${time}`;
}

function isSameDay(first: Date, second: Date) {
	return (
		first.getFullYear() === second.getFullYear() &&
		first.getMonth() === second.getMonth() &&
		first.getDate() === second.getDate()
	);
}

function startOfDay(date: Date) {
	return new Date(
		date.getFullYear(),
		date.getMonth(),
		date.getDate(),
	).getTime();
}

function getCalendarDays(month: Date) {
	const firstDay = new Date(month.getFullYear(), month.getMonth(), 1);
	const start = new Date(firstDay);
	start.setDate(firstDay.getDate() - firstDay.getDay());
	const daysInMonth = new Date(
		month.getFullYear(),
		month.getMonth() + 1,
		0,
	).getDate();
	const cellCount = Math.ceil((firstDay.getDay() + daysInMonth) / 7) * 7;

	return Array.from({ length: cellCount }, (_, index) => {
		const day = new Date(start);
		day.setDate(start.getDate() + index);
		return day;
	});
}

export default function DateTimePicker({
	label,
	value,
	onChange,
	min,
	max,
	align = 'start',
}: DateTimePickerProps) {
	const containerRef = useRef<HTMLDivElement>(null);
	const selectedDate = parseDate(value);
	const [isOpen, setIsOpen] = useState(false);
	const [draftDate, setDraftDate] = useState(selectedDate);
	const [selectionView, setSelectionView] = useState<
		'days' | 'months' | 'years'
	>('days');
	const [visibleMonth, setVisibleMonth] = useState(
		new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1),
	);
	const minDate = min ? parseDate(min) : undefined;
	const maxDate = max ? parseDate(max) : undefined;

	const calendarDays = useMemo(
		() => getCalendarDays(visibleMonth),
		[visibleMonth],
	);
	const monthLabel = visibleMonth.toLocaleDateString(undefined, {
		month: 'long',
	});

	useEffect(() => {
		if (!isOpen) return;

		function handlePointerDown(event: PointerEvent) {
			if (!containerRef.current?.contains(event.target as Node)) {
				setIsOpen(false);
			}
		}

		function handleKeyDown(event: KeyboardEvent) {
			if (event.key === 'Escape') setIsOpen(false);
		}

		document.addEventListener('pointerdown', handlePointerDown);
		document.addEventListener('keydown', handleKeyDown);
		return () => {
			document.removeEventListener('pointerdown', handlePointerDown);
			document.removeEventListener('keydown', handleKeyDown);
		};
	}, [isOpen]);

	function openPicker() {
		const nextDate = parseDate(value);
		setDraftDate(nextDate);
		setVisibleMonth(new Date(nextDate.getFullYear(), nextDate.getMonth(), 1));
		setSelectionView('days');
		setIsOpen(true);
	}

	function changeSelectionPage(offset: number) {
		setVisibleMonth((current) => {
			const yearOffset = selectionView === 'years' ? offset * 12 : offset;
			return new Date(
				current.getFullYear() + yearOffset,
				selectionView === 'days'
					? current.getMonth() + offset
					: current.getMonth(),
				1,
			);
		});
	}

	function selectDay(day: Date) {
		const nextDate = new Date(draftDate);
		nextDate.setFullYear(day.getFullYear(), day.getMonth(), day.getDate());
		setDraftDate(nextDate);
		setVisibleMonth(new Date(day.getFullYear(), day.getMonth(), 1));
		setSelectionView('days');
	}

	function selectMonth(month: number) {
		setVisibleMonth(new Date(visibleMonth.getFullYear(), month, 1));
		setSelectionView('days');
	}

	function selectYear(year: number) {
		setVisibleMonth(new Date(year, visibleMonth.getMonth(), 1));
		setSelectionView('days');
	}

	function updateTime({
		hour12,
		minute,
		meridiem,
	}: Partial<ReturnType<typeof getTimeParts>>) {
		const current = getTimeParts(draftDate);
		const nextHour = hour12 ?? current.hour12;
		const nextMinute = minute ?? current.minute;
		const nextMeridiem = meridiem ?? current.meridiem;
		const nextDate = new Date(draftDate);
		const hour24 = (nextHour % 12) + (nextMeridiem === 'PM' ? 12 : 0);
		nextDate.setHours(hour24, nextMinute, 0, 0);
		setDraftDate(nextDate);
	}

	function applySelection() {
		onChange(toInputValue(draftDate));
		setIsOpen(false);
	}

	return (
		<div ref={containerRef} className="relative min-w-0 flex-1">
			<label
				className="mb-1 block text-sm text-primary"
				htmlFor={`${label}-date`}
			>
				{label}
			</label>
			<button
				type="button"
				id={`${label}-date`}
				className="flex h-10 w-full items-center rounded-control border border-stone-300 px-3 text-left focus-visible:border-primary"
				aria-haspopup="dialog"
				aria-expanded={isOpen}
				onClick={() => (isOpen ? setIsOpen(false) : openPicker())}
			>
				<LuCalendarDays
					size={16}
					className="mr-2 shrink-0 text-carbon-500"
					aria-hidden="true"
				/>
				<span className="truncate text-sm text-carbon-700">
					{formatDateTime(value)}
				</span>
			</button>

			{isOpen && (
				<div
					className={`absolute top-full z-50 mt-2 w-[min(18rem,calc(100vw-2rem))] rounded-panel border border-stone-300 bg-paper-50 p-3 shadow-floating ${align === 'end' ? 'right-0' : 'left-0'}`}
					role="dialog"
					aria-label={`${label} date picker`}
				>
					<div className="flex items-center justify-between">
						<button
							type="button"
							className="grid size-8 place-items-center rounded-control text-carbon-500 hover:bg-primary-soft"
							onClick={() => changeSelectionPage(-1)}
							aria-label="Previous month"
						>
							<LuChevronLeft size={16} />
						</button>
						<div className="flex items-center gap-0">
							<button
								type="button"
								className={`rounded-control px-1 py-1 text-sm font-semibold text-primary ${selectionView === 'months' ? 'bg-primary-soft' : 'hover:bg-primary-soft'}`}
								onClick={() => setSelectionView('months')}
							>
								{monthLabel}
							</button>
							<button
								type="button"
								className={`rounded-control px-1 py-1 text-sm font-semibold text-primary ${selectionView === 'years' ? 'bg-primary-soft' : 'hover:bg-primary-soft'}`}
								onClick={() => setSelectionView('years')}
							>
								{visibleMonth.getFullYear()}
							</button>
						</div>
						<button
							type="button"
							className="grid size-8 place-items-center rounded-control text-carbon-500 hover:bg-primary-soft"
							onClick={() => changeSelectionPage(1)}
							aria-label="Next month"
						>
							<LuChevronRight size={16} />
						</button>
					</div>

					{selectionView === 'days' && (
						<>
							<div className="mt-2 grid grid-cols-7 text-center text-[0.625rem] font-semibold text-carbon-300">
								{WEEKDAYS.map((weekday) => (
									<span key={weekday} className="py-0.5">
										{weekday}
									</span>
								))}
							</div>
							<div className="grid grid-cols-7 gap-0.5">
								{calendarDays.map((day) => {
									const isCurrentMonth =
										day.getMonth() === visibleMonth.getMonth();
									const isSelected = isSameDay(day, draftDate);
									const isToday = isSameDay(day, new Date());
									const dayValue = startOfDay(day);
									const isDisabled =
										(minDate && dayValue < startOfDay(minDate)) ||
										(maxDate && dayValue > startOfDay(maxDate));

									return (
										<button
											key={day.toISOString()}
											type="button"
											disabled={!!isDisabled}
											onClick={() => selectDay(day)}
											className={`grid size-7 place-items-center rounded-control text-[0.6875rem] transition ${
												isSelected
													? 'bg-primary text-paper-50'
													: isDisabled
														? 'cursor-not-allowed text-carbon-300/30'
														: isCurrentMonth
															? 'text-carbon-700 hover:bg-primary-soft'
															: 'text-carbon-300/50 hover:bg-stone-100'
											}`}
											aria-current={isToday ? 'date' : undefined}
											aria-label={day.toLocaleDateString()}
										>
											{day.getDate()}
										</button>
									);
								})}
							</div>
						</>
					)}

					{selectionView === 'months' && (
						<div className="mt-3 grid grid-cols-3 gap-2">
							{Array.from({ length: 12 }, (_, month) => {
								const isSelected = month === visibleMonth.getMonth();
								const label = new Date(2000, month, 1).toLocaleDateString(
									undefined,
									{
										month: 'short',
									},
								);

								return (
									<button
										key={label}
										type="button"
										className={`h-9 rounded-control text-xs ${isSelected ? 'bg-primary text-paper-50' : 'text-carbon-700 hover:bg-primary-soft'}`}
										onClick={() => selectMonth(month)}
									>
										{label}
									</button>
								);
							})}
						</div>
					)}

					{selectionView === 'years' && (
						<div className="mt-3 grid grid-cols-3 gap-2">
							{Array.from({ length: 12 }, (_, index) => {
								const year = visibleMonth.getFullYear() - 5 + index;
								const isSelected = year === visibleMonth.getFullYear();

								return (
									<button
										key={year}
										type="button"
										className={`h-9 rounded-control text-xs ${isSelected ? 'bg-primary text-paper-50' : 'text-carbon-700 hover:bg-primary-soft'}`}
										onClick={() => selectYear(year)}
									>
										{year}
									</button>
								);
							})}
						</div>
					)}

					<div className="mt-3 border-t border-stone-300 pt-3">
						<div className="flex items-center justify-between">
							<span className="text-xs font-semibold text-primary">Time</span>
							<span className="text-[0.6875rem] text-carbon-300">
								Local time
							</span>
						</div>
						<div className="mt-2 grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto] gap-2">
							{(['hour12', 'minute'] as const).map((part) => {
								const time = getTimeParts(draftDate);
								const isHour = part === 'hour12';
								const currentValue = isHour ? time.hour12 : time.minute;
								const label = isHour ? 'Hour' : 'Minute';
								const step = isHour ? 1 : 5;

								return (
									<div key={part}>
										<span className="mb-1 block text-[0.625rem] text-carbon-300">
											{label}
										</span>
										<div className="flex h-8 items-center rounded-control border border-stone-300">
											<button
												type="button"
												className="grid size-7 place-items-center text-carbon-500 hover:bg-primary-soft"
												onClick={() => {
													const maximum = isHour ? 12 : 55;
													const next =
														currentValue - step < (isHour ? 1 : 0)
															? maximum
															: currentValue - step;
													updateTime(
														isHour ? { hour12: next } : { minute: next },
													);
												}}
												aria-label={`Decrease ${label.toLowerCase()}`}
											>
												<LuMinus size={12} />
											</button>
											<span className="min-w-7 text-center font-mono text-xs text-carbon-700">
												{String(currentValue).padStart(2, '0')}
											</span>
											<button
												type="button"
												className="grid size-7 place-items-center text-carbon-500 hover:bg-primary-soft"
												onClick={() => {
													const maximum = isHour ? 12 : 55;
													const minimum = isHour ? 1 : 0;
													const next =
														currentValue + step > maximum
															? minimum
															: currentValue + step;
													updateTime(
														isHour ? { hour12: next } : { minute: next },
													);
												}}
												aria-label={`Increase ${label.toLowerCase()}`}
											>
												<LuPlus size={12} />
											</button>
										</div>
									</div>
								);
							})}
							<div>
								<span className="mb-1 block text-[0.625rem] text-carbon-300">
									Period
								</span>
								<div className="flex h-8 overflow-hidden rounded-control border border-stone-300">
									{(['AM', 'PM'] as const).map((meridiem) => (
										<button
											key={meridiem}
											type="button"
											className={`px-2 text-xs ${getTimeParts(draftDate).meridiem === meridiem ? 'bg-primary text-paper-50' : 'text-carbon-500 hover:bg-primary-soft'}`}
											onClick={() => updateTime({ meridiem })}
										>
											{meridiem}
										</button>
									))}
								</div>
							</div>
						</div>
						<div className="mt-3 flex justify-end gap-1">
							<button
								type="button"
								className="inline-flex h-8 items-center gap-1 rounded-control px-2 text-[0.6875rem] text-carbon-500 hover:bg-primary-soft"
								onClick={() => setIsOpen(false)}
							>
								<LuX size={13} />
								Cancel
							</button>
							<button
								type="button"
								className="inline-flex h-8 items-center gap-1 rounded-control bg-primary px-2 text-[0.6875rem] text-paper-50 hover:bg-carbon-500"
								onClick={applySelection}
							>
								<LuCheck size={13} />
								Apply
							</button>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}
