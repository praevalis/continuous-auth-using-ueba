import Button from '@/components/ui/Button';
import PageHeader from '@/components/ui/PageHeader';

type PoliciesIntroProps = {
	onCreatePolicy: () => void;
};

export default function PoliciesIntro({ onCreatePolicy }: PoliciesIntroProps) {
	return (
		<PageHeader
			eyebrow="Control"
			title="Set the rules for sign-in decisions"
			description="Create and manage the policies that guide continuous authentication responses."
			id="policies-heading"
			className="gap-5"
			trailing={
				<Button
					variant="secondary"
					onClick={onCreatePolicy}
					className="hidden shrink-0 border-primary lg:inline-flex"
				>
					Create policy
				</Button>
			}
		/>
	);
}
