import type { ReactNode } from 'react';
import { cn } from '@/utils/cn';

export default function EmptyState({
	title,
	children,
	action,
	className,
}: {
	title: string;
	children?: ReactNode;
	action?: ReactNode;
	className?: string;
}) {
	return (
		<section className={cn('py-10', className)}>
			<h2 className="text-lg font-semibold text-primary">{title}</h2>
			{children && (
				<div className="mt-2 max-w-xl text-sm text-carbon-500">{children}</div>
			)}
			{action && <div className="mt-4">{action}</div>}
		</section>
	);
}
