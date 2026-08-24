import type { ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import Badge from './Badge';
import { cn } from '@/utils/cn';

const statusBadgeVariants = cva(
	'rounded-control border px-2 py-1 text-xs font-normal',
	{
		variants: {
			tone: {
				safe: 'border-safe/40 bg-safe-soft text-safe',
				caution: 'border-caution/40 bg-caution-soft text-caution',
				lockout: 'border-lockout/40 bg-lockout-soft text-lockout',
				neutral: 'border-neutral/40 bg-neutral-soft text-neutral',
				info: 'border-info/40 bg-info-soft text-info',
			},
			variant: {
				soft: '',
				outline: '',
			},
		},
		compoundVariants: [
			{
				tone: 'safe',
				variant: 'outline',
				className: 'border-safe/60 bg-paper-50 text-safe',
			},
			{
				tone: 'caution',
				variant: 'outline',
				className: 'border-caution/60 bg-paper-50 text-caution',
			},
			{
				tone: 'lockout',
				variant: 'outline',
				className: 'border-lockout/60 bg-paper-50 text-lockout',
			},
			{
				tone: 'neutral',
				variant: 'outline',
				className: 'border-neutral/60 bg-paper-50 text-neutral',
			},
			{
				tone: 'info',
				variant: 'outline',
				className: 'border-info/60 bg-paper-50 text-info',
			},
		],
		defaultVariants: { variant: 'soft' },
	},
);

const statusDotVariants = cva('size-2 rounded-full', {
	variants: {
		tone: {
			safe: 'bg-safe',
			caution: 'bg-caution',
			lockout: 'bg-lockout',
			neutral: 'bg-neutral',
			info: 'bg-info',
		},
	},
});

export type StatusTone = NonNullable<
	VariantProps<typeof statusBadgeVariants>['tone']
>;
export type StatusBadgeVariant = NonNullable<
	VariantProps<typeof statusBadgeVariants>['variant']
>;

export default function StatusBadge({
	children,
	tone,
	leading,
	variant = 'soft',
	showDot = !leading,
	className,
}: {
	children: ReactNode;
	tone: StatusTone;
	leading?: ReactNode;
	variant?: StatusBadgeVariant;
	showDot?: boolean;
	className?: string;
}) {
	return (
		<Badge
			className={cn(statusBadgeVariants({ tone, variant }), className)}
			leading={
				leading ??
				(showDot ? (
					<span className={statusDotVariants({ tone })} aria-hidden="true" />
				) : undefined)
			}
		>
			{children}
		</Badge>
	);
}
