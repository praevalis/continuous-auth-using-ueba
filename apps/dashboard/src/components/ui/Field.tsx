import type { ReactNode } from 'react';
import { cn } from '@/utils/cn';
import InlineError from './InlineError';

export default function Field({
	label,
	children,
	htmlFor,
	required = false,
	hint,
	error,
	className,
}: {
	label: ReactNode;
	children: ReactNode;
	htmlFor?: string;
	required?: boolean;
	hint?: ReactNode;
	error?: ReactNode;
	className?: string;
}) {
	return (
		<div className={cn('grid gap-1.5 text-sm text-primary', className)}>
			<label htmlFor={htmlFor} className="grid gap-1.5">
				<span>
					{label} {required && <span className="text-lockout">*</span>}
				</span>
				{children}
			</label>
			{hint && <p className="text-xs text-carbon-500">{hint}</p>}
			{error && <InlineError className="text-xs">{error}</InlineError>}
		</div>
	);
}
