import { useState } from 'react';
import { LuChevronDown } from 'react-icons/lu';

export type DropdownOption = { label: string; value: string };

type DropdownProps = {
	label: string;
	options: DropdownOption[];
	value?: string;
	onChange?: (..._args: [string]) => void;
};

function Dropdown({ label, options, value, onChange }: DropdownProps) {
	const [isOpen, setIsOpen] = useState(false);
	const selectedOption =
		options.find((option) => option.value === value) ?? options[0];

	return (
		<div className="relative">
			<button
				type="button"
				className="inline-flex items-center gap-2"
				aria-haspopup="listbox"
				aria-expanded={isOpen}
				onClick={() => setIsOpen((open) => !open)}
			>
				{selectedOption?.label ?? label}
				<LuChevronDown size={14} />
			</button>
			{isOpen && (
				<ul
					className="absolute left-0 top-full z-20 mt-2 min-w-40 rounded-panel border border-stone-300 bg-paper-50 p-1 shadow-floating"
					role="listbox"
					aria-label={label}
				>
					{options.map((option) => (
						<li key={option.value}>
							<button
								type="button"
								className="block w-full rounded-control px-3 py-2 text-left text-sm hover:bg-primary-soft"
								role="option"
								aria-selected={option.value === selectedOption?.value}
								onClick={() => {
									onChange?.(option.value);
									setIsOpen(false);
								}}
							>
								{option.label}
							</button>
						</li>
					))}
				</ul>
			)}
		</div>
	);
}

export default Dropdown;
