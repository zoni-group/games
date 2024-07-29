<script lang="ts">
	import DownloadQuiz from '$lib/components/DownloadQuiz.svelte';
	import { getLocalization } from '$lib/i18n';
	import CollapsSection from '$lib/collapsible.svelte';
	import { createTippy } from 'svelte-tippy';
	import ImportedOrNot from '$lib/view_quiz/imported_or_not.svelte';
	import { QuizQuestionType } from '$lib/quiz_types.js';
	import StartGamePopup from '$lib/dashboard/start_game.svelte';
	import { onMount } from 'svelte';
	import Spinner from '$lib/Spinner.svelte';
	import GrayButton from '$lib/components/buttons/gray.svelte';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import RatingComponent from '$lib/view_quiz/RatingComponent.svelte';
	import { page } from '$app/stores';
	import ModComponent from './ModComponent.svelte';
	import { get_foreground_color } from '$lib/helpers.ts';
	import playIcon from "$lib/assets/all/play.svg";

	const default_colors = ['#C8E6C9', '#FFE0B2', '#FFF9C4', '#B3E5FC'];

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'right'
	});

	let start_game = null;
	let download_id: string | null = null;
	const urlparams = $page.url.searchParams;
	const mod_view = Boolean(urlparams.get('mod'));
	const auto_expand = Boolean(urlparams.get('autoExpand'));
	const auto_return = Boolean(urlparams.get('autoReturn'));
	console.log(auto_expand, 'autoexpand');
	const close_start_game_if_esc_is_pressed = (key: KeyboardEvent) => {
		if (key.code === 'Escape') {
			start_game = null;
		}
	};
	onMount(() => {
		document.body.addEventListener('keydown', close_start_game_if_esc_is_pressed);
	});

	const { t } = getLocalization();
	export let data;
	let { quiz, logged_in }: { quiz: QuizData; logged_in: boolean } = data;
	let contentType: string | null = null;

	interface Question {
		time: string;
		question: string;
		image?: string;
		answers: Answer[];
	}

	interface Answer {
		right: boolean;
		answer: string;
	}

	interface QuizData {
		id: string;
		public: boolean;
		title: string;
		description: string;
		created_at: string;
		updated_at: string;
		user_id: string;
		imported_from_kahoot?: boolean;
		questions: Question[];
		kahoot_id?: string;
		mod_rating?: number;
		cover_image: string;
	}

	async function fetchContentType(url: string) {
		const response = await fetch(url, {
			method: 'HEAD'
		});
		return response.headers.get('Content-Type');
	}

	onMount(async () => {
		if (quiz.cover_image) {
			contentType = await fetchContentType(`/api/v1/storage/download/${quiz.cover_image}`);
		}
	});

	// Function to ensure the .mp4 extension is present
	function getVideoUrl(url) {
		if (!url.endsWith('.mp4')) {
			return `${url}.mp4`;
		}
		return url;
	}

	// Function to ensure the .mp3 extension is present
	function getAudioUrl(url) {
		if (!url.endsWith('.mp3')) {
			return `${url}.mp3`;
		}
		return url;
	}
</script>

<svelte:head>
	<title>Zoni® AI - View {quiz.title}</title>
</svelte:head>

<div>
	<h1 class="text-4xl text-center text-white">{@html quiz.title}</h1>
	<div class="text-center">
		<p class="text-white" >{@html quiz.description}</p>
	</div>
	<p class="text-center text-white">
		<small>
			{$t('view_quiz_page.made_by')}
			<a href="/user/{quiz.user_id.id}" class="underline text-blue-600 dark:text-blue-300">@{quiz.user_id.username}</a>
		</small>
	</p>
	{#if quiz.cover_image}
		<div class="flex justify-center align-middle items-center">
			<div class=" m-auto w-4/5 my-3 p-4">
				{#if contentType?.startsWith('image')}
					<img
						class="max-h-full max-w-full block rounded-2xl"
						src={`/api/v1/storage/download/${quiz.cover_image}`}
						alt="Not provided"
					/>
				{:else if contentType?.startsWith('video')}
					<!-- svelte-ignore a11y-media-has-caption -->
					<video
						class="max-h-full max-w-full block rounded-2xl"
						src={getVideoUrl(`/api/v1/storage/download/${quiz.cover_image}`)}
						controls
						autoplay={false}
						loop={false}
					>
						Your browser does not support the video tag.
					</video>
				{:else if contentType?.startsWith('audio')}
					<div class="flex items-center justify-center h-full w-full">
						<!-- svelte-ignore a11y-media-has-caption -->
						<audio controls autoplay={false} loop={false} preload="auto" class="w-full">
							<source src={getAudioUrl(`/api/v1/storage/download/${quiz.cover_image}`)} type="audio/mpeg" />
							Your browser does not support the audio element.
						</audio>
					</div>
				{:else}
					<p>Unsupported media type</p>
				{/if}
			</div>
		</div>
	{/if}
	<!--
	<div class="text-center text-sm pt-1 mb-4">
		<ImportedOrNot imported={quiz.imported_from_kahoot} />
	</div>
	-->
	<div class="grid md:grid-cols-2 grid-cols-1 items-center">
		<div class="flex md:justify-end justify-center mb-2 flex-row gap-2">
			<RatingComponent bind:quiz />
			{#if mod_view}
				<ModComponent autoReturn={auto_return} quiz_id={quiz.id} />
			{/if}
		</div>
		<div class="flex md:justify-start justify-center justify-items-start mb-2 flex-row gap-2">
			<div class="ml-5 flex flex-col gap-2 justify-start justify-items-start">
				{#if quiz.imported_from_kahoot && quiz.kahoot_id}
					<div class="w-full flex justify-center">
						<GrayButton
							href="https://create.kahoot.it/details/{quiz.kahoot_id}"
							target="_blank"
						>
							{$t('view_quiz_page.view_on_kahoot')}
						</GrayButton>
					</div>
				{/if}
				{#if logged_in}
					<div class="w-full flex justify-center">
						<button 
							on:click={() => {
								start_game = quiz.id;
							}}
							class="flex bg-gradient-to-r from-amber-600 items-center justify-center gap-3 font-bold style-text md:text-2xl  via-yellow-300 to-amber-500 px-4 py-2 rounded-full border-4 border-[#0AEDFE]"
						>
							<img src="{playIcon}" alt="">
							{$t('words.start')}
						</button>
					</div>
				{:else}
					<div use:tippy={{ content: $t('words.you_need_to_be_logged_in_to_start_a_game')}}>
						<div class="w-full flex justify-center">
							<GrayButton disabled={true} flex={true}>
								<!-- heroicons/legacy-outline/Play -->
								<svg xmlns="http://www.w3.org/2000/svg" height="20" width="20" viewBox="0 0 512 512"><!--!Font Awesome Pro 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2024 Fonticons, Inc.--><path class="fa-secondary" opacity=".4" fill="#808080" d="M0 256a256 256 0 1 1 512 0A256 256 0 1 1 0 256zM188.3 147.1c-7.6 4.2-12.3 12.3-12.3 20.9V344c0 8.7 4.7 16.7 12.3 20.9s16.8 4.1 24.3-.5l144-88c7.1-4.4 11.5-12.1 11.5-20.5s-4.4-16.1-11.5-20.5l-144-88c-7.4-4.5-16.7-4.7-24.3-.5z"/><path class="fa-primary" fill="#ffffff" d="M212.5 147.5c-7.4-4.5-16.7-4.7-24.3-.5s-12.3 12.3-12.3 20.9V344c0 8.7 4.7 16.7 12.3 20.9s16.8 4.1 24.3-.5l144-88c7.1-4.4 11.5-12.1 11.5-20.5s-4.4-16.1-11.5-20.5l-144-88z"/></svg>
								{$t('words.start')}
							</GrayButton>
						</div>
					</div>
				{/if}
				{#if logged_in}
					<div class="w-full flex justify-center my-3">
						<a href="/practice?quiz_id={quiz.id}" class="flex text-white underline text-2xl">
							<!-- <svg xmlns="http://www.w3.org/2000/svg" height="20" width="20" viewBox="0 0 512 512">!Font Awesome Pro 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2024 Fonticons, Inc.<path class="fa-secondary" opacity="1" fill="#ffffff" d="M305.4 21.8c-1.3-10.4-9.1-18.8-19.5-20C276.1 .6 266.1 0 256 0c-11.1 0-22.1 .7-32.8 2.1c-10.3 1.3-18 9.7-19.3 20l-2.9 23.1c-.8 6.4-5.4 11.6-11.5 13.7c-9.6 3.2-19 7.2-27.9 11.7c-5.8 3-12.8 2.5-18-1.5l-18-14c-8.2-6.4-19.7-6.8-27.9-.4c-16.6 13-31.5 28-44.4 44.7c-6.3 8.2-5.9 19.6 .5 27.8l14.2 18.3c4 5.1 4.4 12 1.5 17.8c-4.4 8.8-8.2 17.9-11.3 27.4c-2 6.2-7.3 10.8-13.7 11.6l-22.8 2.9c-10.3 1.3-18.7 9.1-20 19.4C.7 234.8 0 245.3 0 256c0 10.6 .6 21.1 1.9 31.4c1.3 10.3 9.7 18.1 20 19.4l22.8 2.9c6.4 .8 11.7 5.4 13.7 11.6c3.1 9.5 6.9 18.7 11.3 27.5c2.9 5.8 2.4 12.7-1.5 17.8L54 384.8c-6.4 8.2-6.8 19.6-.5 27.8c12.9 16.7 27.8 31.7 44.4 44.7c8.2 6.4 19.7 6 27.9-.4l18-14c5.1-4 12.2-4.4 18-1.5c9 4.6 18.3 8.5 27.9 11.7c6.1 2.1 10.7 7.3 11.5 13.7l2.9 23.1c1.3 10.3 9 18.7 19.3 20c10.7 1.4 21.7 2.1 32.8 2.1c10.1 0 20.1-.6 29.9-1.7c10.4-1.2 18.2-9.7 19.5-20l2.8-22.5c.8-6.5 5.5-11.8 11.7-13.8c10-3.2 19.7-7.2 29-11.8c5.8-2.9 12.7-2.4 17.8 1.5L385 457.9c8.2 6.4 19.6 6.8 27.8 .5c2.8-2.2 5.5-4.4 8.2-6.7L451.7 421c1.8-2.2 3.6-4.4 5.4-6.6c6.5-8.2 6-19.7-.4-27.9l-14-17.9c-4-5.1-4.4-12.2-1.5-18c4.8-9.4 9-19.3 12.3-29.5c2-6.2 7.3-10.8 13.7-11.6l22.8-2.8c10.3-1.3 18.8-9.1 20-19.4c.2-1.7 .4-3.5 .6-5.2V230.1c-.2-1.7-.4-3.5-.6-5.2c-1.3-10.3-9.7-18.1-20-19.4l-22.8-2.8c-6.4-.8-11.7-5.4-13.7-11.6c-3.4-10.2-7.5-20.1-12.3-29.5c-3-5.8-2.5-12.8 1.5-18l14-17.9c6.4-8.2 6.8-19.7 .4-27.9c-1.8-2.2-3.6-4.4-5.4-6.6L421 60.3c-2.7-2.3-5.4-4.5-8.2-6.7c-8.2-6.4-19.6-5.9-27.8 .5L366.7 68.3c-5.1 4-12.1 4.4-17.8 1.5c-9.3-4.6-19-8.6-29-11.8c-6.2-2-10.9-7.3-11.7-13.7l-2.8-22.5zM287.8 162.6l-32 192c-1.5 8.7-9.7 14.6-18.4 13.2s-14.6-9.7-13.2-18.4l32-192c1.5-8.7 9.7-14.6 18.4-13.2s14.6 9.7 13.2 18.4zM187.3 227.3L158.6 256l28.7 28.7c6.2 6.2 6.2 16.4 0 22.6s-16.4 6.2-22.6 0l-40-40c-6.2-6.2-6.2-16.4 0-22.6l40-40c6.2-6.2 16.4-6.2 22.6 0s6.2 16.4 0 22.6zm160-22.6l40 40c6.2 6.2 6.2 16.4 0 22.6l-40 40c-6.2 6.2-16.4 6.2-22.6 0s-6.2-16.4 0-22.6L353.4 256l-28.7-28.7c-6.2-6.2-6.2-16.4 0-22.6s16.4-6.2 22.6 0z"/><path class="fa-primary" fill="#004a93" d="M274.6 144.2c8.7 1.5 14.6 9.7 13.2 18.4l-32 192c-1.5 8.7-9.7 14.6-18.4 13.2s-14.6-9.7-13.2-18.4l32-192c1.5-8.7 9.7-14.6 18.4-13.2zm-87.3 60.5c6.2 6.2 6.2 16.4 0 22.6L158.6 256l28.7 28.7c6.2 6.2 6.2 16.4 0 22.6s-16.4 6.2-22.6 0l-40-40c-6.2-6.2-6.2-16.4 0-22.6l40-40c6.2-6.2 16.4-6.2 22.6 0zm137.4 0c6.2-6.2 16.4-6.2 22.6 0l40 40c6.2 6.2 6.2 16.4 0 22.6l-40 40c-6.2 6.2-16.4 6.2-22.6 0s-6.2-16.4 0-22.6L353.4 256l-28.7-28.7c-6.2-6.2-6.2-16.4 0-22.6z"/></svg> -->
							{$t('words.practice')}
						</a>
					</div>
				{:else}
					<div use:tippy={{ content: $t('words.you_need_to_be_logged_in_to_start_a_practice')}}>
						<div class="w-full flex justify-center">
							<button disabled={true}  class="flex text-white underline text-2xl" >
								<!-- <svg xmlns="http://www.w3.org/2000/svg" height="20" width="20" viewBox="0 0 512 512">!Font Awesome Pro 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2024 Fonticons, Inc.<path class="fa-secondary" opacity="1" fill="#ffffff" d="M305.4 21.8c-1.3-10.4-9.1-18.8-19.5-20C276.1 .6 266.1 0 256 0c-11.1 0-22.1 .7-32.8 2.1c-10.3 1.3-18 9.7-19.3 20l-2.9 23.1c-.8 6.4-5.4 11.6-11.5 13.7c-9.6 3.2-19 7.2-27.9 11.7c-5.8 3-12.8 2.5-18-1.5l-18-14c-8.2-6.4-19.7-6.8-27.9-.4c-16.6 13-31.5 28-44.4 44.7c-6.3 8.2-5.9 19.6 .5 27.8l14.2 18.3c4 5.1 4.4 12 1.5 17.8c-4.4 8.8-8.2 17.9-11.3 27.4c-2 6.2-7.3 10.8-13.7 11.6l-22.8 2.9c-10.3 1.3-18.7 9.1-20 19.4C.7 234.8 0 245.3 0 256c0 10.6 .6 21.1 1.9 31.4c1.3 10.3 9.7 18.1 20 19.4l22.8 2.9c6.4 .8 11.7 5.4 13.7 11.6c3.1 9.5 6.9 18.7 11.3 27.5c2.9 5.8 2.4 12.7-1.5 17.8L54 384.8c-6.4 8.2-6.8 19.6-.5 27.8c12.9 16.7 27.8 31.7 44.4 44.7c8.2 6.4 19.7 6 27.9-.4l18-14c5.1-4 12.2-4.4 18-1.5c9 4.6 18.3 8.5 27.9 11.7c6.1 2.1 10.7 7.3 11.5 13.7l2.9 23.1c1.3 10.3 9 18.7 19.3 20c10.7 1.4 21.7 2.1 32.8 2.1c10.1 0 20.1-.6 29.9-1.7c10.4-1.2 18.2-9.7 19.5-20l2.8-22.5c.8-6.5 5.5-11.8 11.7-13.8c10-3.2 19.7-7.2 29-11.8c5.8-2.9 12.7-2.4 17.8 1.5L385 457.9c8.2 6.4 19.6 6.8 27.8 .5c2.8-2.2 5.5-4.4 8.2-6.7L451.7 421c1.8-2.2 3.6-4.4 5.4-6.6c6.5-8.2 6-19.7-.4-27.9l-14-17.9c-4-5.1-4.4-12.2-1.5-18c4.8-9.4 9-19.3 12.3-29.5c2-6.2 7.3-10.8 13.7-11.6l22.8-2.8c10.3-1.3 18.8-9.1 20-19.4c.2-1.7 .4-3.5 .6-5.2V230.1c-.2-1.7-.4-3.5-.6-5.2c-1.3-10.3-9.7-18.1-20-19.4l-22.8-2.8c-6.4-.8-11.7-5.4-13.7-11.6c-3.4-10.2-7.5-20.1-12.3-29.5c-3-5.8-2.5-12.8 1.5-18l14-17.9c6.4-8.2 6.8-19.7 .4-27.9c-1.8-2.2-3.6-4.4-5.4-6.6L421 60.3c-2.7-2.3-5.4-4.5-8.2-6.7c-8.2-6.4-19.6-5.9-27.8 .5L366.7 68.3c-5.1 4-12.1 4.4-17.8 1.5c-9.3-4.6-19-8.6-29-11.8c-6.2-2-10.9-7.3-11.7-13.7l-2.8-22.5zM287.8 162.6l-32 192c-1.5 8.7-9.7 14.6-18.4 13.2s-14.6-9.7-13.2-18.4l32-192c1.5-8.7 9.7-14.6 18.4-13.2s14.6 9.7 13.2 18.4zM187.3 227.3L158.6 256l28.7 28.7c6.2 6.2 6.2 16.4 0 22.6s-16.4 6.2-22.6 0l-40-40c-6.2-6.2-6.2-16.4 0-22.6l40-40c6.2-6.2 16.4-6.2 22.6 0s6.2 16.4 0 22.6zm160-22.6l40 40c6.2 6.2 6.2 16.4 0 22.6l-40 40c-6.2 6.2-16.4 6.2-22.6 0s-6.2-16.4 0-22.6L353.4 256l-28.7-28.7c-6.2-6.2-6.2-16.4 0-22.6s16.4-6.2 22.6 0z"/><path class="fa-primary" fill="#004a93" d="M274.6 144.2c8.7 1.5 14.6 9.7 13.2 18.4l-32 192c-1.5 8.7-9.7 14.6-18.4 13.2s-14.6-9.7-13.2-18.4l32-192c1.5-8.7 9.7-14.6 18.4-13.2zm-87.3 60.5c6.2 6.2 6.2 16.4 0 22.6L158.6 256l28.7 28.7c6.2 6.2 6.2 16.4 0 22.6s-16.4 6.2-22.6 0l-40-40c-6.2-6.2-6.2-16.4 0-22.6l40-40c6.2-6.2 16.4-6.2 22.6 0zm137.4 0c6.2-6.2 16.4-6.2 22.6 0l40 40c6.2 6.2 6.2 16.4 0 22.6l-40 40c-6.2 6.2-16.4 6.2-22.6 0s-6.2-16.4 0-22.6L353.4 256l-28.7-28.7c-6.2-6.2-6.2-16.4 0-22.6z"/></svg> -->
								{$t('words.practice')}
							</button>
						</div>
					</div>
				{/if}
				<div class="w-full flex justify-center">
					{#if logged_in}
						<!-- svelte-ignore a11y-click-events-have-key-events -->
						<p on:click={() => (download_id = quiz.id)}  class="flex text-white underline text-2xl">
							<!-- <svg
								class="w-5 h-5 inline-block"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
								/>
							</svg> -->
							{$t('words.download')}
						</p>
					{:else}
						<div use:tippy={{ content: $t('words.you_need_to_be_logged_in_to_download_a_game') }}>
							<GrayButton disabled={true} flex={true}>
								<svg xmlns="http://www.w3.org/2000/svg" height="20" width="15" viewBox="0 0 384 512"><!--!Font Awesome Pro 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2024 Fonticons, Inc.--><path class="fa-secondary" opacity="1" fill="#ffffff" d="M0 64C0 28.7 28.7 0 64 0H224V128c0 17.7 14.3 32 32 32H384V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zM216 232c0-13.3-10.7-24-24-24s-24 10.7-24 24V334.1l-31-31c-9.4-9.4-24.6-9.4-33.9 0s-9.4 24.6 0 33.9l72 72c9.4 9.4 24.6 9.4 33.9 0l72-72c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-31 31V232z"/><path class="fa-primary" opacity="1" fill="#004a93" d="M384 160L224 0V128c0 17.7 14.3 32 32 32H384zM216 232c0-13.3-10.7-24-24-24s-24 10.7-24 24V334.1l-31-31c-9.4-9.4-24.6-9.4-33.9 0s-9.4 24.6 0 33.9l72 72c9.4 9.4 24.6 9.4 33.9 0l72-72c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-31 31V232z"/></svg>
								{$t('words.download')}
							</GrayButton>
						</div>
					{/if}
				</div>
				<div class="w-full flex justify-center my-3">
					<a
						href="mailto:operez@zoni.edu?subject=Report activity {quiz.id}"
						  class="flex text-white underline text-xl"
					>
						{$t('words.report')}
					</a>
				</div>
			</div>
		</div>
	</div>
	<div class="mb-5" >
		{#if logged_in}
			{#each quiz.questions as question, index_question}
				<div class="px-4 py-1">
					<CollapsSection headerText={question.question} expanded={auto_expand}>
						<div class="grid grid-cols-1 gap-2 rounded-b-lg bg-white dark:bg-gray-700 -mt-1">
							<h3 class="text-3xl m-1 text-center text-black dark:text-white">
								{index_question + 1}: {@html question.question}
							</h3>
	
							<!--					<label class='m-1 flex flex-row gap-2 w-3/5'>-->
	
							<!--					</label>-->
							{#if question.image}
								<span>
									<MediaComponent
										css_classes="mx-auto"
										src={question.image}
										muted={false}
									/>
								</span>
							{/if}
							<p
								class="m-1 flex flex-row gap-2 flex-nowrap whitespace-nowrap w-full justify-center text-gray-800 dark:text-gray-200"
							>
								<svg
									class="w-8 h-8 inline-block"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
									xmlns="http://www.w3.org/2000/svg"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
								<span class="text-lg">{question.time}s</span>
							</p>
							{#if question.type === QuizQuestionType.ABCD || question.type === undefined || question.type === QuizQuestionType.CHECK}
								<div class="grid grid-cols-2 gap-4 m-4 p-6">
									{#each question.answers as answer, index_answer}
										<div
											class="p-1 rounded-lg py-4 shadow-xl"
											style="background-color: {answer.color ??
												default_colors[index_answer]}; color: {get_foreground_color(
												answer.color ?? default_colors[index_answer]
											)}"
											class:shadow-blue-500={answer.right &&
												question.type !== QuizQuestionType.VOTING}
											class:shadow-yellow-500={!answer.right &&
												question.type !== QuizQuestionType.VOTING}
										>
											<h4 class="text-center text-white">
												{quiz.questions[index_question].answers[index_answer]
													.answer}
											</h4>
										</div>
									{/each}
								</div>
							{:else if question.type === QuizQuestionType.RANGE}
								<p class="m-1 text-center text-gray-800 dark:text-gray-200">
									All numbers between {question.answers.min_correct}
									and {question.answers.max_correct} are correct, where numbers between {question
										.answers.min} and {question.answers.max} can be selected.
								</p>
							{:else if question.type === QuizQuestionType.ORDER}
								<ul class="flex flex-col gap-4 m-4 p-6">
									{#each question.answers as answer}
										<li class="p-1 rounded-lg py-3 dark:bg-gray-500 bg-gray-300" style="background-color: {answer.color ??
										default_colors[index_answer]}; color: {get_foreground_color(
										answer.color ?? default_colors[index_answer]
									)}">
											<h4 class="text-center text-black dark:text-white">
												{answer.answer}
											</h4>
										</li>
									{/each}
								</ul>
							{:else if question.type === QuizQuestionType.VOTING || question.type === QuizQuestionType.TEXT}
								<div class="grid grid-cols-2 gap-4 m-4 p-6">
									{#each question.answers as answer, index_answer}
										<div class="p-1 rounded-lg py-4 dark:bg-gray-500 bg-gray-300" 
										style="background-color: {answer.color ??
										default_colors[index_answer]}; color: {get_foreground_color(
										answer.color ?? default_colors[index_answer]
									)}">
											<h4 class="text-center text-black dark:text-white">
												{quiz.questions[index_question].answers[index_answer]
													.answer}
											</h4>
										</div>
									{/each}
								</div>
							{:else if question.type === QuizQuestionType.SLIDE}
								{#await import('$lib/play/admin/slide.svelte')}
									<Spinner my={false} />
								{:then c}
									<div class="max-h-[90%] max-w-[90%]">
										<svelte:component this={c.default} bind:question />
									</div>
								{/await}
							{/if}
						</div>
					</CollapsSection>
				</div>
			{/each}
		{/if}
	</div>
</div>

{#if start_game !== null}
	<StartGamePopup bind:quiz_id={start_game} />
{/if}

<DownloadQuiz bind:quiz_id={download_id} />
<style>
	.style-text{
		-webkit-text-stroke: 1px #70158F;
		color: white;

		
	}
</style>