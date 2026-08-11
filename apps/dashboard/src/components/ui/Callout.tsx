import type { ReactNode } from 'react';
import { cn } from '@/utils/cn';

type CalloutProps = {
	title: string;
	children: ReactNode;
	className?: string;
};

export default function Callout({
	title,
	children,
	className = '',
}: CalloutProps) {
	return (
		<aside
			className={cn(
				'rounded-panel bg-stone-100/70 px-5 py-5 sm:px-6',
				className,
			)}
		>
			<div className="rounded-sm border-l-4 border-primary pl-4">
				<h2 className="text-lg font-semibold text-primary">{title}</h2>
				<div className="mt-2 leading-6">{children}</div>
			</div>
		</aside>
	);
}
