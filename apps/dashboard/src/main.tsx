import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import '@fontsource/dm-sans/400.css';
import '@fontsource/dm-sans/500.css';
import '@fontsource/dm-sans/600.css';
import '@fontsource/ibm-plex-mono/400.css';
import './index.css';
import App from './App';

const rootElement = document.getElementById('root');

if (!rootElement) {
	throw new Error('Root element was not found.');
}

createRoot(rootElement).render(
	<StrictMode>
		<App />
	</StrictMode>,
);
