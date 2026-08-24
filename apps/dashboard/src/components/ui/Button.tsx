import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/utils/cn';

const buttonVariants = cva(
	'inline-flex items-center justify-center gap-2 rounded-control font-sans transition focus-visible:outline-none focus-visible:ring-2 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-transparent',
	{
		variants: {
			variant: {
				primary:
					'border border-primary bg-primary text-paper-50 hover:bg-carbon-500 focus-visible:ring-primary',
				secondary:
					'border border-stone-300 text-primary hover:bg-primary-soft focus-visible:ring-primary',
				quiet: 'text-primary hover:bg-primary-soft focus-visible:ring-primary',
				danger:
					'border border-lockout/50 text-lockout hover:bg-lockout-soft focus-visible:ring-lockout',
			},
			size: {
				sm: 'min-h-8 px-3 py-1.5 text-xs',
				md: 'min-h-10 px-4 py-2 text-sm',
				lg: 'min-h-11 px-5 py-2.5 text-sm',
			},
		},
		defaultVariants: { variant: 'secondary', size: 'md' },
	},
);

export type ButtonVariant = NonNullable<
	VariantProps<typeof buttonVariants>['variant']
>;
export type ButtonSize = NonNullable<
	VariantProps<typeof buttonVariants>['size']
>;

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> &
	VariantProps<typeof buttonVariants> & {
		asChild?: boolean;
		loading?: boolean;
		leading?: ReactNode;
		trailing?: ReactNode;
	};

export default function Button({
	variant = 'secondary',
	size = 'md',
	loading = false,
	leading,
	trailing,
	children,
	className,
	type = 'button',
	disabled,
	asChild = false,
	...props
}: ButtonProps) {
	const Comp = asChild ? Slot : 'button';

	return (
		<Comp
			{...props}
			{...(!asChild && {
				type,
				disabled: disabled || loading,
			})}
			aria-busy={loading || undefined}
			className={cn(buttonVariants({ variant, size }), className)}
		>
			{loading ? (
				<span
					className="size-3.5 animate-spin rounded-full border-2 border-current border-t-transparent"
					aria-hidden="true"
				/>
			) : (
				leading
			)}
			{children}
			{trailing}
		</Comp>
	);
}
