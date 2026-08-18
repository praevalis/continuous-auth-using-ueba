import { useEffect, useRef, useState } from 'react';
import { LuChevronDown } from 'react-icons/lu';

export type DropdownOption = { label: string; value: string };

type DropdownProps = {
	label: string;
	options: DropdownOption[];
	value?: string;
	onChange?: (..._args: [string]) => void;
	fullWidth?: boolean;
};

function Dropdown({
	label,
	options,
	value,
	onChange,
	fullWidth = false,
}: DropdownProps) {
	const [isOpen, setIsOpen] = useState(false);
	const containerRef = useRef<HTMLDivElement>(null);
	const selectedOption =
		options.find((option) => option.value === value) ?? options[0];

	useEffect(() => {
		if (!isOpen) return;
		const handlePointerDown = (event: PointerEvent) => {
			if (!containerRef.current?.contains(event.target as Node))
				setIsOpen(false);
		};
		document.addEventListener('pointerdown', handlePointerDown);
		return () => document.removeEventListener('pointerdown', handlePointerDown);
	}, [isOpen]);

	return (
		<div
			ref={containerRef}
			className={`relative ${fullWidth ? 'h-full w-full' : ''}`}
		>
			<button
				type="button"
				className={`inline-flex items-center gap-2 ${fullWidth ? 'h-full w-full justify-between px-3' : ''}`}
				aria-haspopup="listbox"
				aria-expanded={isOpen}
				onClick={() => setIsOpen((open) => !open)}
			>
				{selectedOption?.label ?? label}
				<LuChevronDown size={14} />
			</button>
			{isOpen && (
				<ul
					className={`absolute left-0 top-full z-50 mt-2 rounded-panel border border-stone-300 p-1 shadow-floating ${fullWidth ? 'w-full bg-paper-100' : 'min-w-40 bg-paper-50'}`}
					role="listbox"
					aria-label={label}
				>
					{options.map((option) => (
						<li key={option.value}>
							<button
								type="button"
								className="block w-full rounded-control px-3 py-2 text-left text-xs hover:bg-primary-soft lg:text-sm"
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
