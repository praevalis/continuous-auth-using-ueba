import { useEffect, useRef, useState } from 'react';
import { LuChevronDown } from 'react-icons/lu';
import { NavLink } from 'react-router-dom';

export type DropdownOption = { label: string; value: string };
export type DropdownLink = { label: string; to: string };

type DropdownProps = {
	label: string;
	options: DropdownOption[];
	value?: string;
	onChange?: (..._args: [string]) => void;
	fullWidth?: boolean;
	id?: string;
	links?: DropdownLink[];
	align?: 'start' | 'end';
	buttonClassName?: string;
	scrollable?: boolean;
};

function Dropdown({
	label,
	options,
	value,
	onChange,
	fullWidth = false,
	id,
	links = [],
	align = 'start',
	buttonClassName = '',
	scrollable = false,
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
				id={id}
				type="button"
				className={`inline-flex items-center gap-2 ${fullWidth ? 'h-full w-full justify-between px-3' : ''} ${buttonClassName}`}
				aria-haspopup="listbox"
				aria-expanded={isOpen}
				onClick={() => setIsOpen((open) => !open)}
			>
				{selectedOption?.label ?? label}
				<LuChevronDown size={14} />
			</button>
			{isOpen && (
				<ul
					className={`absolute top-full z-50 mt-2 max-w-[calc(100vw-2rem)] rounded-panel border border-stone-300 bg-paper-50 p-1 shadow-floating ${align === 'end' ? 'right-0' : 'left-0'} ${fullWidth ? 'w-full bg-paper-100' : links.length > 0 ? 'w-56' : 'min-w-40'} ${scrollable ? 'max-h-[190px] overflow-y-auto [scrollbar-color:theme(colors.primary.soft)_transparent] [scrollbar-width:thin] [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-primary-soft [&::-webkit-scrollbar-track]:bg-transparent' : ''}`}
					role="listbox"
					aria-label={label}
				>
					{options.map((option) => (
						<li key={option.value}>
							<button
								type="button"
								className={`block w-full rounded-control px-3 py-2 text-left text-xs hover:bg-primary-soft lg:text-sm ${scrollable ? 'h-9' : ''}`}
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
					{links.length > 0 && (
						<>
							<li
								className="my-1 border-t border-stone-300"
								aria-hidden="true"
							/>
							{links.map((link) => (
								<li key={link.to}>
									<NavLink
										to={link.to}
										className="block rounded-control px-3 py-2 text-left text-xs hover:bg-primary-soft lg:text-sm"
										onClick={() => setIsOpen(false)}
									>
										{link.label}
									</NavLink>
								</li>
							))}
						</>
					)}
				</ul>
			)}
		</div>
	);
}

export default Dropdown;
