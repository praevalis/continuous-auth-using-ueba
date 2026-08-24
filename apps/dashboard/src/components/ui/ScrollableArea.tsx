import type { HTMLAttributes } from 'react';
import { cn } from '@/utils/cn';

export default function ScrollableArea({
	className,
	...props
}: HTMLAttributes<HTMLDivElement>) {
	return (
		<div
			{...props}
			className={cn(
				'threat-feed-scrollbar overflow-y-auto [scrollbar-color:theme(colors.primary.soft)_transparent] [scrollbar-width:thin] [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-primary-soft [&::-webkit-scrollbar-track]:bg-transparent',
				className,
			)}
		/>
	);
}
