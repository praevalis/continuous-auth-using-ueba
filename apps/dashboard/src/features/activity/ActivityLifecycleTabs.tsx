import { LuSearch, LuZap } from 'react-icons/lu';
import type { ActivityKind, ActivitySection } from './types';

function ExclamationIcon({ size = 19 }: { size?: number }) {
	return (
		<span
			className="font-semibold leading-none"
			style={{ fontSize: size }}
			aria-hidden="true"
		>
			!
		</span>
	);
}

const icons = {
	analysis: LuSearch,
	decisions: ExclamationIcon,
	response: LuZap,
};

export default function ActivityLifecycleTabs({
	sections,
	selectedId,
	onSelect,
}: {
	sections: ActivitySection[];
	selectedId: ActivityKind;
	onSelect: (_id: ActivityKind) => void;
}) {
	return (
		<div
			className="grid grid-cols-3 border-b border-stone-300"
			role="tablist"
			aria-label="Activity lifecycle"
			aria-orientation="horizontal"
		>
			{sections.map((section) => {
				const Icon = icons[section.id];
				const isSelected = section.id === selectedId;

				return (
					<button
						key={section.id}
						type="button"
						role="tab"
						aria-selected={isSelected}
						id={`${section.id}-activity-tab`}
						aria-controls={`${section.id}-activity-panel`}
						tabIndex={isSelected ? 0 : -1}
						className={`relative flex min-h-14 items-center justify-center gap-1 px-1 text-left text-[0.75rem] transition sm:gap-3 sm:px-2 sm:text-sm ${
							isSelected
								? 'font-semibold text-primary after:absolute after:inset-x-0 after:bottom-[-1px] after:h-px after:bg-carbon-300'
								: 'text-carbon-300 hover:text-primary'
						}`}
						onClick={() => onSelect(section.id)}
						onKeyDown={(event) => {
							if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight')
								return;
							event.preventDefault();
							const direction = event.key === 'ArrowRight' ? 1 : -1;
							const nextIndex =
								(sections.findIndex((item) => item.id === section.id) +
									direction +
									sections.length) %
								sections.length;
							onSelect(sections[nextIndex].id);
						}}
					>
						<span
							className={`grid size-6 shrink-0 place-items-center sm:size-9 ${
								section.id === 'analysis'
									? 'text-primary'
									: section.id === 'decisions'
										? 'text-caution'
										: 'text-safe'
							}`}
						>
							<Icon size={19} />
						</span>
						<span className="truncate">{section.title}</span>
					</button>
				);
			})}
		</div>
	);
}
