import { LuRefreshCw } from 'react-icons/lu';
import { cn } from '@/utils/cn';
import Button from './Button';

export default function ResourceError({
	title,
	error,
	onRetry,
	className,
}: {
	title: string;
	error: string | Error;
	onRetry?: () => void;
	className?: string;
}) {
	const message = typeof error === 'string' ? error : error.message;

	return (
		<section
			className={cn(
				'rounded-panel border border-lockout/30 bg-lockout-soft/30 px-5 py-4 sm:px-6',
				className,
			)}
			role="alert"
		>
			<div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
				<div className="min-w-0">
					<h2 className="text-base font-semibold text-lockout">{title}</h2>
					<p className="mt-1 text-sm text-carbon-700">{message}</p>
				</div>
				{onRetry && (
					<Button
						size="sm"
						onClick={onRetry}
						leading={<LuRefreshCw size={14} aria-hidden="true" />}
						className="self-start border-primary text-sm sm:self-auto"
					>
						Retry
					</Button>
				)}
			</div>
		</section>
	);
}
