import type { HTMLAttributes } from 'react';
import { cn } from '@/utils/cn';

export function Skeleton({
	className,
	...props
}: HTMLAttributes<HTMLSpanElement>) {
	return (
		<span
			aria-hidden="true"
			{...props}
			className={cn('block animate-pulse rounded bg-stone-200', className)}
		/>
	);
}

export function SkeletonText({
	className,
	...props
}: HTMLAttributes<HTMLSpanElement>) {
	return <Skeleton {...props} className={cn('h-4', className)} />;
}

export function SkeletonCircle({
	className,
	...props
}: HTMLAttributes<HTMLSpanElement>) {
	return (
		<Skeleton {...props} className={cn('size-10 rounded-full', className)} />
	);
}

export function SkeletonControl({
	className,
	...props
}: HTMLAttributes<HTMLSpanElement>) {
	return (
		<Skeleton {...props} className={cn('h-10 rounded-control', className)} />
	);
}
