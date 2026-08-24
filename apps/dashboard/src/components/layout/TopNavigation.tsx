import { useCallback, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { BsBuildingFill } from 'react-icons/bs';
import { LuMenu, LuX } from 'react-icons/lu';
import logo from '@/assets/logo.svg';
import Dropdown from '@/components/ui/Dropdown';
import IconButton from '@/components/ui/IconButton';
import { useTenant } from '@/hooks/useTenant';
import type { OperatingModeValue } from '@/api/contracts';
import { useOperatingModes, usePolicyModeMutation } from '@/hooks';
import { useBodyScrollLock } from '@/hooks/useBodyScrollLock';
import {
	operatingModeLabels,
	operatingModeOptions,
} from '@/utils/operatingMode';

const navigationItems = [
	{ label: 'Overview', to: '/' },
	{ label: 'Threat feed', to: '/threat-feed' },
	{ label: 'Policies', to: '/policies' },
	{ label: 'Activity', to: '/activity' },
];

const tenantSettingsLinks = [
	{ label: 'Tenant settings', to: '/settings/tenant' },
	{ label: 'Event sources & credentials', to: '/settings/event-sources' },
	{ label: 'Provider connections', to: '/settings/providers' },
];
function TenantDropdown({
	options,
	value,
	onChange,
	align = 'start',
}: {
	options: Array<{ label: string; value: string }>;
	value?: string;
	onChange: (_value: string) => void;
	align?: 'start' | 'end';
}) {
	return (
		<div className="flex min-w-0 items-center gap-2">
			<BsBuildingFill
				className="shrink-0 text-primary"
				size={14}
				aria-hidden="true"
			/>
			<Dropdown
				label="Tenant"
				options={options}
				links={tenantSettingsLinks}
				value={value}
				onChange={onChange}
				align={align}
			/>
		</div>
	);
}

function MobileNavigation({
	onClose,
	responseMode,
	responseModeDisabled,
	onResponseModeChange,
}: {
	onClose: () => void;
	responseMode?: OperatingModeValue;
	responseModeDisabled: boolean;
	onResponseModeChange: (..._args: [string]) => void;
}) {
	const { tenant } = useTenant();
	useBodyScrollLock(true);
	return (
		<div
			className="fixed inset-0 z-50 md:hidden"
			role="dialog"
			aria-modal="true"
			aria-label="Mobile navigation"
		>
			<button
				type="button"
				className="absolute inset-0 bg-carbon-700/20"
				onClick={onClose}
				aria-label="Close navigation"
			/>
			<aside className="absolute right-0 top-0 flex h-full w-[min(86vw,320px)] flex-col bg-paper-50 px-6 py-4 text-carbon-700 shadow-floating">
				<div className="flex items-center justify-between border-b border-stone-300 pb-4">
					<div className="flex items-center gap-3 text-lg font-semibold tracking-[-0.02em] text-primary">
						<img className="size-9" src={logo} alt="" />
						Continuous Auth
					</div>
					<IconButton
						icon={<LuX size={24} aria-hidden="true" />}
						label="Close navigation"
						onClick={onClose}
						variant="quiet"
						size="sm"
						className="size-10 p-2 text-primary"
					/>
				</div>
				<nav className="mt-6" aria-label="Mobile navigation links">
					<p className="text-xs font-semibold uppercase tracking-[0.12em] text-carbon-300">
						Pages
					</p>
					<div className="mt-3">
						{navigationItems.map((item) => (
							<NavLink
								key={item.to}
								to={item.to}
								end={item.to === '/'}
								onClick={onClose}
								className={({ isActive }) =>
									`block border-l-2 px-4 py-2.5 text-sm ${isActive ? 'border-primary bg-primary-soft font-semibold text-primary' : 'border-transparent'}`
								}
							>
								{item.label}
							</NavLink>
						))}
					</div>
				</nav>
				<section
					className="mt-2 pt-5"
					aria-labelledby="mobile-simulation-heading"
				>
					<h2
						id="mobile-simulation-heading"
						className="text-xs font-semibold uppercase tracking-[0.12em] text-carbon-300"
					>
						Simulation
					</h2>
					<div className="mt-4 h-10 rounded-control border border-stone-300">
						<Dropdown
							label="Response mode"
							options={responseMode ? operatingModeOptions : []}
							value={responseMode}
							onChange={onResponseModeChange}
							fullWidth
							buttonClassName="text-sm text-primary"
							disabled={responseModeDisabled}
						/>
					</div>
				</section>
				<section className="mt-2 pt-5" aria-labelledby="mobile-tenant-heading">
					<h2
						id="mobile-tenant-heading"
						className="text-xs font-semibold uppercase tracking-[0.12em] text-carbon-300"
					>
						Tenant
					</h2>
					<div className="mt-4">
						<div className="flex items-center gap-2 px-4 text-sm font-medium text-primary">
							<BsBuildingFill size={14} aria-hidden="true" />
							<span className="truncate">
								{tenant?.display_name ?? 'No tenant selected'}
							</span>
						</div>
						<div className="mt-3">
							{tenantSettingsLinks.map((item) => (
								<NavLink
									key={item.to}
									to={item.to}
									onClick={onClose}
									className={({ isActive }) =>
										`block border-l-2 px-4 py-2.5 text-sm ${isActive ? 'border-primary bg-primary-soft font-semibold text-primary' : 'border-transparent'}`
									}
								>
									{item.label}
								</NavLink>
							))}
						</div>
					</div>
				</section>
			</aside>
		</div>
	);
}

export default function TopNavigation() {
	const [isMenuOpen, setIsMenuOpen] = useState(false);
	const { tenant, tenants, setTenantId } = useTenant();
	const {
		data: operatingModeData,
		loading: operatingModesLoading,
		error: operatingModesError,
		refresh: refreshOperatingModes,
	} = useOperatingModes(tenant?.id);
	const { mutateAsync: mutateOperatingMode, pending: operatingModePending } =
		usePolicyModeMutation(tenant?.id);
	const tenantOptions = tenants.map((item) => ({
		label: item.display_name,
		value: item.id,
	}));
	const responseMode = operatingModeData?.find((mode) => mode.is_active)?.mode;
	const responseModeDisabled =
		operatingModesLoading ||
		!!operatingModesError ||
		!responseMode ||
		operatingModePending;
	const handleResponseModeChange = useCallback(
		async (value: string) => {
			if (
				!tenant?.id ||
				!responseMode ||
				value === responseMode ||
				!(value in operatingModeLabels)
			)
				return;

			try {
				await mutateOperatingMode({
					mode: value as OperatingModeValue,
					effective_from: new Date().toISOString(),
				});
				await refreshOperatingModes();
			} catch {
				// The current mode remains selected when the update fails.
			}
		},
		[mutateOperatingMode, refreshOperatingModes, responseMode, tenant?.id],
	);

	return (
		<header className="border-b border-stone-300/80 bg-paper-50">
			<div className="mx-auto flex max-w-375 items-center gap-5 px-4 py-4 sm:px-8 lg:px-12">
				<NavLink
					className="flex shrink-0 items-center gap-3 text-lg font-semibold tracking-[-0.02em] text-primary"
					to="/"
					aria-label="Continuous Auth overview"
				>
					<img className="size-9" src={logo} alt="" />
					<span>Continuous Auth</span>
				</NavLink>
				<div className="hidden h-7 w-px bg-stone-300 md:block" />
				<div className="hidden items-center gap-6 text-sm md:flex">
					<div className="h-10 w-40">
						<Dropdown
							label="Response mode"
							options={responseMode ? operatingModeOptions : []}
							value={responseMode}
							onChange={(value) => void handleResponseModeChange(value)}
							fullWidth
							buttonClassName="text-sm text-primary"
							disabled={responseModeDisabled}
						/>
					</div>
					<span className="h-6 w-px bg-stone-300" />
				</div>
				<div className="ml-auto hidden items-center text-sm md:flex">
					<TenantDropdown
						options={tenantOptions}
						value={tenant?.id}
						onChange={setTenantId}
						align="end"
					/>
				</div>
				<IconButton
					icon={<LuMenu size={28} aria-hidden="true" />}
					label="Open navigation"
					onClick={() => setIsMenuOpen(true)}
					variant="quiet"
					size="sm"
					className="ml-auto size-10 p-1 text-primary md:hidden"
				/>
			</div>
			<nav
				className="mx-auto hidden max-w-375 gap-10 px-4 sm:px-8 lg:px-12 md:flex"
				aria-label="Primary navigation"
			>
				{navigationItems.map((item) => (
					<NavLink
						key={item.to}
						to={item.to}
						end={item.to === '/'}
						className={({ isActive }) =>
							`border-b-2 px-1 py-3 text-sm ${isActive ? 'border-primary font-semibold text-primary' : 'border-transparent text-carbon-700'}`
						}
					>
						{item.label}
					</NavLink>
				))}
			</nav>
			{isMenuOpen && (
				<MobileNavigation
					onClose={() => setIsMenuOpen(false)}
					responseMode={responseMode}
					responseModeDisabled={responseModeDisabled}
					onResponseModeChange={(value) => void handleResponseModeChange(value)}
				/>
			)}
		</header>
	);
}
