import type { ReactNode } from 'react';
import { cn } from '@/utils/cn';
import SectionEyebrow, { type SectionEyebrowTone } from './SectionEyebrow';

type PageHeaderProps = {
	eyebrow: string;
	eyebrowTone?: SectionEyebrowTone;
	title: string;
	description: string;
	trailing?: ReactNode;
	id?: string;
	className?: string;
};

export default function PageHeader({
	eyebrow,
	eyebrowTone = 'info',
	title,
	description,
	trailing,
	id,
	className,
}: PageHeaderProps) {
	return (
		<section
			className={cn(
				'flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between',
				className,
			)}
			aria-labelledby={id}
		>
			<div>
				<SectionEyebrow tone={eyebrowTone}>{eyebrow}</SectionEyebrow>
				<h1
					id={id}
					className="mt-2 max-w-4xl text-3xl font-semibold leading-tight tracking-[-0.035em] text-primary sm:text-4xl"
				>
					{title}
				</h1>
				<p className="mt-3 max-w-2xl text-base text-carbon-300">
					{description}
				</p>
			</div>
			{trailing}
		</section>
	);
}
