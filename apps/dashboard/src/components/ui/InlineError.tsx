import type { ReactNode } from 'react';
import { cn } from '@/utils/cn';

export default function InlineError({
	children,
	className,
}: {
	children: ReactNode;
	className?: string;
}) {
	return (
		<p className={cn('text-sm text-lockout', className)} role="alert">
			{children}
		</p>
	);
}
