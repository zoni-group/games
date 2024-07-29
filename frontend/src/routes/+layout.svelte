<script>
	import '../app.css';
	import Navbar from '$lib/navbar.svelte';
	import { navbarVisible, pathname } from '$lib/stores';
	import * as Sentry from '@sentry/browser';
	import { BrowserTracing } from '@sentry/tracing';
	import { initLocalizationContext } from '$lib/i18n';
	import CommandPalette from '$lib/components/commandpalette.svelte';
	import { SvelteToast } from '@zerodevx/svelte-toast';
	import { browser } from "$app/environment";

	const plausible_data_url = import.meta.env.VITE_PLAUSIBLE_DATA_URL;

	if (browser) {
		pathname.set(window.location.pathname);
		const theme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
		if (theme === 'dark') {
			document.documentElement.classList.add('dark');
		} else {
			document.documentElement.classList.remove('dark');
		}
	}

	initLocalizationContext();

	if (import.meta.env.VITE_SENTRY !== undefined && import.meta.env.PROD) {
		Sentry.init({
			dsn: String(import.meta.env.VITE_SENTRY),
			integrations: [new BrowserTracing()],
			tracesSampleRate: 0.5
		});
	}

	const options = {
		duration: 4000,
		theme: {
			'--toastBackground': '#333',
			'--toastColor': '#fff',
		}
	};
</script>

<svelte:head>
	{#if plausible_data_url}
		<link rel="prefetch" href="https://sugar.mawoka.eu.org/" />
		<script
			async=""
			defer=""
			data-domain={plausible_data_url}
			src="https://sugar.mawoka.eu.org/js/plausible.hash.outbound-links.js"
		></script>
		<script>
			window.plausible =
				window.plausible ||
				function () {
					(window.plausible.q = window.plausible.q || []).push(arguments);
				};
		</script>
	{/if}
</svelte:head>

<SvelteToast {options} />
{#if $navbarVisible}
	<Navbar />
	<div class="pt-16 flex flex-col h-screen">
		<div class="z-40 flex-1 overflow-y-auto">
			<slot />
		</div>
	</div>
{:else}
	<div class="flex flex-col h-screen">
		<div class="flex-1 overflow-y-auto">
			<slot />
		</div>
	</div>
{/if}
<CommandPalette />

<style lang="scss">

	:global(html.dark){
		background-image: url('$lib/assets/all/bg_dark.webp') !important;
		background-position: center;
		background-repeat: no-repeat;
		background-size: cover;
	}
	:global(html:not(.dark)) {
		background-image: url('$lib/assets/all/bg.webp');
		background-position: center;
		background-repeat: no-repeat;
		background-size: cover;
	}

	:global(html.dark) {
		background-color: #383838;
		color: white;

		:global(#pips-slider) {
			--pip: white;
			--pip-active: white;
		}
	}

	@keyframes background_animation {
		0% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
		100% {
			background-position: 0% 50%;
		}
	}
</style>
