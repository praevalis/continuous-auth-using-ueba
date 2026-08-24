import type { ReactNode } from 'react';
import { LuX } from 'react-icons/lu';
import { useBodyScrollLock } from '@/hooks/useBodyScrollLock';
import SectionEyebrow from './SectionEyebrow';
import IconButton from './IconButton';

type ModalProps = {
	eyebrow: string;
	title: string;
	titleId: string;
	onClose: () => void;
	closeDisabled?: boolean;
	children: ReactNode;
};

export default function Modal({
	eyebrow,
	title,
	titleId,
	onClose,
	closeDisabled = false,
	children,
}: ModalProps) {
	useBodyScrollLock(true);

	return (
		<div
			className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-primary/20 px-4 py-4 sm:items-center"
			role="presentation"
			onClick={(event) => {
				if (event.target === event.currentTarget) onClose();
			}}
		>
			<div
				className="w-full max-w-xl rounded-panel bg-paper-50 p-4 shadow-floating sm:p-5"
				role="dialog"
				aria-modal="true"
				aria-labelledby={titleId}
			>
				<div className="flex items-start justify-between gap-4">
					<div>
						<SectionEyebrow>{eyebrow}</SectionEyebrow>
						<h2
							id={titleId}
							className="mt-2 text-lg font-semibold text-primary"
						>
							{title}
						</h2>
					</div>
					<IconButton
						icon={<LuX size={18} aria-hidden="true" />}
						label="Close dialog"
						onClick={onClose}
						disabled={closeDisabled}
						variant="quiet"
						size="sm"
						className="size-10 p-2 text-carbon-500"
					/>
				</div>
				<div className="mt-4">{children}</div>
			</div>
		</div>
	);
}
