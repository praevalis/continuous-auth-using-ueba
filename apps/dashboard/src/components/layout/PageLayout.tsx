import type { ReactNode } from 'react';

type PageLayoutProps = {
	title: string;
	children: ReactNode;
};

function PageLayout({ title, children }: PageLayoutProps) {
	return (
		<main
			className="mx-auto min-h-svh w-full max-w-375 px-4 pb-12 pt-10 sm:px-8 lg:px-12 lg:pt-12"
			aria-labelledby={`${title.toLowerCase().replaceAll(' ', '-')}-page-title`}
		>
			<h1
				id={`${title.toLowerCase().replaceAll(' ', '-')}-page-title`}
				className="sr-only"
			>
				{title}
			</h1>
			{children}
		</main>
	);
}

export default PageLayout;
