import type { ReactNode } from 'react';
import { cn } from '@/utils/cn';
import Button, { type ButtonProps } from './Button';

type IconButtonProps = Omit<
	ButtonProps,
	'children' | 'leading' | 'trailing'
> & {
	icon: ReactNode;
	label: string;
};

export default function IconButton({ icon, label, ...props }: IconButtonProps) {
	return (
		<Button
			{...props}
			aria-label={label}
			title={props.title ?? label}
			className={cn('size-10 p-0', props.className)}
		>
			{icon}
		</Button>
	);
}
