<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { navbarVisible } from '$lib/stores';
	import { getLocalization } from '$lib/i18n';
	import Footer from '$lib/footer.svelte';
	import WebPOpenGraph from '$lib/assets/landing/opengraph-home.webp';
	import JpgOpenGraph from '$lib/assets/landing/opengraph-home.jpg';
	import { fly, fade } from 'svelte/transition';

	/*	import LandingPromo from '$lib/landing/landing-promo.svelte';*/

	import { onMount } from 'svelte';

	const { t } = getLocalization();

	navbarVisible.set(true);

	/*	interface StatsData {
		quiz_count: number;
		user_count: number;
	}*/

	/*	const getStats = async (): Promise<StatsData> => {
			const response = await fetch('/api/v1/stats/combined');
			return await response.json();
		};*/

	// eslint-disable-next-line no-unused-vars
	enum SelectedCreateThing {
		// eslint-disable-next-line no-unused-vars
		Create,
		// eslint-disable-next-line no-unused-vars
		Find,
		// eslint-disable-next-line no-unused-vars
		Import
	}

	// eslint-disable-next-line no-unused-vars
	enum SelectedPlayThing {
		// eslint-disable-next-line no-unused-vars
		Select,
		// eslint-disable-next-line no-unused-vars
		Results,
		// eslint-disable-next-line no-unused-vars
		Winners
	}

	let selected_create_thing = SelectedCreateThing.Create;
	let selected_play_thing = SelectedPlayThing.Select;

	/*	<li>No;
		Tracking < /li>
		< li > Self - hostable < /li>
		< li > German;
		Server < /li>
		< li > user - friendly < /li>
		< li > Completely;
		free < /li>
		< li > Quiz - results;
		are;
		downloadable < /li>;*/

	const classquiz_reasons = [
		{
			headline: $t('index_page.no_player_limit'),
			content: $t('index_page.no_player_limit_content')
		},
		{
			headline: $t('index_page.no_tracking'),
			content: $t('index_page.no_tracking_content')
		},
		{
			headline: $t('index_page.self_hostable'),
			content: $t('index_page.self_hostable_content')
		},
		{
			headline: $t('index_page.german_server'),
			content: $t('index_page.german_server_content')
		},
		{
			headline: $t('index_page.user_friendly'),
			content: $t('index_page.user_friendly_content')
		},
		{
			headline: $t('index_page.completely_free'),
			content: $t('index_page.completely_free_content')
		},
		{
			headline: $t('index_page.quiz_results_downloadable'),
			content: $t('index_page.quiz_results_downloadable_content')
		},
		{
			headline: $t('index_page.multilingual'),
			content: $t('index_page.multilingual_content')
		},
		{
			headline: $t('index_page.dark_mode'),
			content: $t('index_page.dark_mode_content')
		},
		{
			headline: $t('index_page.download_quizzes'),
			content: $t('index_page.download_quizzes_content')
		},
		{
			headline: $t('index_page.community_driven'),
			content: $t('index_page.community_driven_content')
		}
	];
	let selected_classquiz_reason = 0;
</script>

<svelte:head>
	<title>Zoni® AI - {$t('index_page.meta.title')}</title>
	<meta name="description" content={$t('index_page.meta.description')} />
	<title>Zoni® AI - Home</title>
	<meta
		name="description"
		content="At Zoni, our commitment to providing exceptional learning."
	/>

	<meta property="og:url" content="https://classquiz.de/" />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="ClassQuiz - {$t('index_page.meta.title')}" />
	<meta
		property="og:description"
		content="At Zoni, our commitment to providing exceptional learning."
	/>
	<meta property="og:image" content={JpgOpenGraph} />

	<meta name="twitter:card" content="summary_large_image" />
	<meta property="twitter:domain" content="classquiz.de" />
	<meta property="twitter:url" content="https://classquiz.de/" />
	<meta name="twitter:title" content="Zoni AI - {$t('index_page.meta.title')}" />
	<meta
		name="twitter:description"
		content="At Zoni, our commitment to providing exceptional learning."
	/>
	<meta name="twitter:image" content={WebPOpenGraph} />
</svelte:head>

<Footer />

<style>
	.why-classquiz::-webkit-scrollbar {
		height: 0.8rem;
		margin-bottom: 5rem;
	}

	.why-classquiz::-webkit-scrollbar-track {
		box-shadow: inset 0 0 10px 10px transparent;
		border: solid 3px transparent;
	}

	.why-classquiz::-webkit-scrollbar-thumb {
		box-shadow: inset 0 0 10px 10px #374151;
		border: solid 3px transparent;
		border-radius: 15px;
	}

	.why-classquiz::-webkit-scrollbar-thumb:hover {
		box-shadow: inset 0 0 10px 10px #555;
		border: solid 3px transparent;
	}
</style>
