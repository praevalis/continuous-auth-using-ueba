import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { LuClock3, LuMenu, LuX } from 'react-icons/lu';
import logo from '@/assets/logo.svg';
import Dropdown from '@/components/ui/Dropdown';
import { useTenant } from '@/api/tenant';

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
const responseModeOptions = [
	{ label: 'Simulation', value: 'simulation' },
	{ label: 'Notify only', value: 'notify-only' },
	{ label: 'Active response', value: 'active-response' },
];

function MobileNavigation({ onClose }: { onClose: () => void }) {
	const { tenant, tenants, setTenantId } = useTenant();
	const tenantOptions = tenants.map((item) => ({
		label: item.display_name,
		value: item.id,
	}));
	return (
		<div
			className="fixed inset-0 z-50 md:hidden"
			role="dialog"
			aria-modal="true"
			aria-label="Mobile navigation"
		>
			<button
				className="absolute inset-0 bg-carbon-700/20"
				onClick={onClose}
				aria-label="Close navigation"
			/>
			<aside className="absolute right-0 top-0 flex h-full w-[min(86vw,320px)] flex-col bg-paper-50 px-6 py-5 text-carbon-700 shadow-floating">
				<div className="flex items-center justify-between border-b border-stone-300 pb-5">
					<div className="flex items-center gap-3 text-lg font-semibold tracking-[-0.02em] text-primary">
						<img className="size-9" src={logo} alt="" />
						Continuous Auth
					</div>
					<button
						className="grid size-10 place-items-center text-primary"
						onClick={onClose}
						aria-label="Close navigation"
					>
						<LuX size={24} />
					</button>
				</div>
				<nav className="mt-6" aria-label="Mobile navigation links">
					{navigationItems.map((item) => (
						<NavLink
							key={item.to}
							to={item.to}
							end={item.to === '/'}
							onClick={onClose}
							className={({ isActive }) =>
								`block border-l-2 px-4 py-3 text-base ${isActive ? 'border-primary bg-primary-soft font-semibold text-primary' : 'border-transparent'}`
							}
						>
							{item.label}
						</NavLink>
					))}
				</nav>
				<div className="mt-8 border-t border-stone-300 pt-5 text-sm">
					<p className="text-xs font-semibold uppercase tracking-[0.12em] text-carbon-300">
						Context
					</p>
					<div className="mt-4 space-y-4">
						<Dropdown
							label="Tenant"
							options={tenantOptions}
							links={tenantSettingsLinks}
							value={tenant?.id}
							onChange={setTenantId}
						/>
						<Dropdown label="Response mode" options={responseModeOptions} />
						<div className="flex items-center gap-2 text-carbon-300">
							<LuClock3 size={15} /> Updated 12s ago
						</div>
					</div>
				</div>
			</aside>
		</div>
	);
}

export default function TopNavigation() {
	const [isMenuOpen, setIsMenuOpen] = useState(false);
	const { tenant, tenants, setTenantId } = useTenant();
	const tenantOptions = tenants.map((item) => ({
		label: item.display_name,
		value: item.id,
	}));

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
					<Dropdown label="Response mode" options={responseModeOptions} />
					<span className="h-6 w-px bg-stone-300" />
					<span className="flex items-center gap-2 text-carbon-300">
						<LuClock3 size={15} /> Updated 12s ago
					</span>
				</div>
				<div className="ml-auto hidden items-center text-sm md:flex">
					<Dropdown
						label="Tenant"
						options={tenantOptions}
						links={tenantSettingsLinks}
						value={tenant?.id}
						onChange={setTenantId}
						align="end"
					/>
				</div>
				<button
					className="ml-auto grid size-10 place-items-center text-primary md:hidden"
					onClick={() => setIsMenuOpen(true)}
					aria-label="Open navigation"
				>
					<LuMenu size={28} />
				</button>
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
			{isMenuOpen && <MobileNavigation onClose={() => setIsMenuOpen(false)} />}
		</header>
	);
}
