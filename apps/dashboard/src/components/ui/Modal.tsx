import type { ReactNode } from 'react';
import { LuX } from 'react-icons/lu';

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
	return (
		<div
			className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-primary/20 px-4 py-4 sm:items-center"
			role="presentation"
		>
			<div
				className="w-full max-w-xl rounded-panel bg-paper-50 p-4 shadow-floating sm:p-5"
				role="dialog"
				aria-modal="true"
				aria-labelledby={titleId}
			>
				<div className="flex items-start justify-between gap-4">
					<div>
						<div className="flex items-center gap-3 text-label uppercase tracking-[0.12em] text-carbon-300">
							<span
								className="h-1 w-5 rounded-full bg-info"
								aria-hidden="true"
							/>
							<span>{eyebrow}</span>
							<span
								className="h-1 w-5 rounded-full bg-info"
								aria-hidden="true"
							/>
						</div>
						<h2
							id={titleId}
							className="mt-2 text-lg font-semibold text-primary"
						>
							{title}
						</h2>
					</div>
					<button
						type="button"
						onClick={onClose}
						disabled={closeDisabled}
						aria-label="Close dialog"
						className="rounded-control p-2 text-carbon-500 transition hover:bg-primary-soft disabled:cursor-not-allowed disabled:opacity-50"
					>
						<LuX size={18} aria-hidden="true" />
					</button>
				</div>
				<div className="mt-4">{children}</div>
			</div>
		</div>
	);
}
