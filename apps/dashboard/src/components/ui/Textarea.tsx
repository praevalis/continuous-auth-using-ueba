import type { TextareaHTMLAttributes } from 'react';
import { cn } from '@/utils/cn';

type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement>;

export default function Textarea({ className, ...props }: TextareaProps) {
	return (
		<textarea
			{...props}
			className={cn(
				'h-18 resize-none overflow-x-hidden overflow-y-auto py-1.5 [scrollbar-color:theme(colors.primary.soft)_transparent] [scrollbar-width:thin] [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-primary-soft [&::-webkit-scrollbar-track]:bg-transparent',
				'w-full appearance-none rounded-control border border-stone-300 bg-transparent px-3 font-sans text-sm text-carbon-700 outline-none transition-colors placeholder:text-carbon-300 focus:border-stone-300 focus:outline-none focus:ring-0 focus-visible:border-stone-300 focus-visible:outline-none focus-visible:ring-0 disabled:cursor-not-allowed disabled:opacity-50',
				className,
			)}
		/>
	);
}
