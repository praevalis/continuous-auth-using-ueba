import type { InputHTMLAttributes } from 'react';
import { cn } from '@/utils/cn';

type InputProps = InputHTMLAttributes<HTMLInputElement>;

export default function Input({ className, ...props }: InputProps) {
	return (
		<input
			{...props}
			className={cn(
				'h-9 w-full appearance-none rounded-control border border-stone-300 bg-transparent px-3 font-sans text-sm text-carbon-700 outline-none transition-colors placeholder:text-carbon-300 focus:border-stone-300 focus:outline-none focus:ring-0 focus-visible:border-stone-300 focus-visible:outline-none focus-visible:ring-0 disabled:cursor-not-allowed disabled:opacity-50',
				'[&::-webkit-inner-spin-button]:m-0 [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:m-0 [&::-webkit-outer-spin-button]:appearance-none',
				className,
			)}
		/>
	);
}
