import type { ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/utils/cn';

const eyebrowLineVariants = cva('h-1 w-5 rounded-full', {
	variants: {
		tone: {
			safe: 'bg-safe',
			caution: 'bg-caution',
			lockout: 'bg-lockout',
			info: 'bg-info',
		},
	},
	defaultVariants: { tone: 'info' },
});

export type SectionEyebrowTone = NonNullable<
	VariantProps<typeof eyebrowLineVariants>['tone']
>;

export default function SectionEyebrow({
	children,
	tone = 'info',
	className,
}: {
	children: ReactNode;
	tone?: SectionEyebrowTone;
	className?: string;
}) {
	return (
		<div className={cn('flex items-center gap-3 text-carbon-300', className)}>
			<span className={eyebrowLineVariants({ tone })} aria-hidden="true" />
			<span className="text-label uppercase tracking-[0.12em]">{children}</span>
			<span className={eyebrowLineVariants({ tone })} aria-hidden="true" />
		</div>
	);
}
