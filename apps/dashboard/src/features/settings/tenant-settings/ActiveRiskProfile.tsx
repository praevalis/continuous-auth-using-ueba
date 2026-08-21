import SegmentedBar from '@/components/ui/SegmentedBar';
import type { ThresholdProfile } from './types';

export default function ActiveRiskProfile({
	profile,
}: {
	profile: ThresholdProfile;
}) {
	const cautionPosition = `${profile.caution_threshold * 100}%`;
	const lockoutPosition = `${profile.lockout_threshold * 100}%`;
	const safeWidth = `${profile.caution_threshold * 100}%`;
	const cautionWidth = `${(profile.lockout_threshold - profile.caution_threshold) * 100}%`;
	const lockoutWidth = `${(1 - profile.lockout_threshold) * 100}%`;

	return (
		<div className="min-w-0 border-t border-stone-300 pt-8 lg:border-l lg:border-t-0 lg:pl-8 lg:pt-0">
			<h2 className="text-section-title text-primary">Active risk profile</h2>
			<dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
				<dt className="text-carbon-700">{profile.name}</dt>
				<dd className="text-primary">
					{profile.is_active ? 'Active' : 'Inactive'}
				</dd>
				<dt className="text-carbon-700">Caution threshold</dt>
				<dd className="text-primary">{profile.caution_threshold.toFixed(3)}</dd>
				<dt className="text-carbon-700">Lockout threshold</dt>
				<dd className="text-primary">{profile.lockout_threshold.toFixed(3)}</dd>
			</dl>
			<div className="mt-6">
				<SegmentedBar
					items={[
						{ label: 'Safe', value: safeWidth, className: 'bg-safe' },
						{ label: 'Caution', value: cautionWidth, className: 'bg-caution' },
						{ label: 'Lockout', value: lockoutWidth, className: 'bg-lockout' },
					]}
				/>
				<div className="relative mt-2 h-5 text-[0.6875rem] text-carbon-500 lg:text-xs">
					<span className="absolute left-0">0.000</span>
					<span
						className="absolute -translate-x-1/2"
						style={{ left: cautionPosition }}
					>
						{profile.caution_threshold.toFixed(3)}
					</span>
					<span
						className="absolute -translate-x-1/2"
						style={{ left: lockoutPosition }}
					>
						{profile.lockout_threshold.toFixed(3)}
					</span>
					<span className="absolute right-0">1.000</span>
				</div>
				<div className="mt-1 grid grid-cols-3 text-xs text-primary">
					<span>Safe</span>
					<span className="text-center">Caution</span>
					<span className="text-right">Lockout</span>
				</div>
			</div>
		</div>
	);
}
