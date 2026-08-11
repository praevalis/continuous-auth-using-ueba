import type { ReactNode } from 'react';
import { cn } from '@/utils/cn';

type BadgeProps = {
	children: ReactNode;
	leading?: ReactNode;
	className?: string;
};

export default function Badge({
	children,
	leading,
	className = '',
}: BadgeProps) {
	return (
		<span className={cn('inline-flex items-center gap-1.5', className)}>
			{leading}
			{children}
		</span>
	);
}
