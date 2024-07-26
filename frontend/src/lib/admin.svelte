<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import { get_question_title } from '$lib/admin.ts';
	import type { PlayerAnswer } from '$lib/admin.ts';
	import { socket } from './socket';
	import { QuizQuestionType } from '$lib/quiz_types';
	import Spinner from '$lib/Spinner.svelte';
	import Controls from '$lib/play/admin/controls.svelte';
	import Question from '$lib/play/admin/question.svelte';
	import { onMount } from 'svelte';

	export let game_token: string;
	export let quiz_data: QuizData;
	export let game_mode: string;
	export let bg_color: string;

	const { t } = getLocalization();
	const default_colors = ['#FFA800', '#FF1D38', '#00A3FF', '#00D749'];

	let question_results = null;
	export let final_results: Array<null> | Array<Array<PlayerAnswer>> = [null];
	let selected_question = -1;
	let timer_res: string;
	let shown_question_now: number;
	let final_results_clicked = false;
	let timer_interval;
	let answer_count = 0;
	export let control_visible: boolean;

	export let player_scores;
	let contentType: string | null = null;
	async function fetchContentType(url: string) {
		const response = await fetch(url, {
			method: 'HEAD'
		});
		return response.headers.get('Content-Type');
	}

	onMount(async () => {
		if (quiz_data.cover_image) {
			contentType = await fetchContentType(`/api/v1/storage/download/${quiz_data.cover_image}`);
		}
	});

	socket.on('get_question_results', () => {
		console.log('get_question_results');
	});
	socket.on('set_question_number', (data) => {
		timer_res = '0';
		clearInterval(timer_interval);
		question_results = null;
		shown_question_now = data.question_index;
		timer_res = quiz_data.questions[data.question_index].time;
		selected_question = selected_question + 1;
		answer_count = 0;
		timer(timer_res);
	});

	socket.on('solutions', (_) => {
		timer_res = '0';
		clearInterval(timer_interval);
	});

	socket.on('final_results', (data) => {
		// data = JSON.parse(data);
		final_results_clicked = true;
		timer_res = '0';
		final_results = data;
	});

	socket.on('everyone_answered', (_) => {
		timer_res = '0';
	});

	socket.on('question_results', (data) => {
		console.log('question_results:', data);
		question_results = data;
		timer_res = '0';
	});

	socket.on('player_answer', (_) => {
		answer_count += 1;
	});

	const timer = (time: string) => {
		let seconds = Number(time);
		timer_interval = setInterval(() => {
			if (timer_res === '0') {
				clearInterval(timer_interval);
				// socket.emit('show_solutions', {});
				return;
			} else {
				seconds--;
			}

			timer_res = seconds.toString();
		}, 1000);
	};

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

{#if control_visible}
	<Controls
		{bg_color}
		{selected_question}
		{quiz_data}
		{answer_count} 
		bind:timer_res
		{final_results}
		{socket}
		{question_results}
		{game_token}
		{shown_question_now}
	/>
{/if}
{#if timer_res !== '0' && selected_question >= 0}
	<span
		class="fixed top-0 bg-red-500 h-8 transition-all"
		class:mt-10={control_visible}
		style="width: {(100 / parseInt(quiz_data.questions[selected_question].time)) *
			parseInt(timer_res)}vw"
	/>
{/if}

<div class="w-full h-full" class:pt-28={control_visible} class:pt-12={!control_visible}>
	{#if timer_res !== undefined && !final_results_clicked && !question_results}
		<!-- Question is shown -->
		{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
			{#await import('$lib/play/admin/slide.svelte')}
				<Spinner my_20={false} />
			{:then c}
				<svelte:component
					this={c.default}
					bind:question={quiz_data.questions[selected_question]}
				/>
			{/await}
		{:else}
			<Question {quiz_data} {selected_question} {timer_res} {answer_count} {default_colors} />
		{/if}
	{/if}
	<br />
	{#if timer_res === '0' && JSON.stringify(final_results) === JSON.stringify( [null] ) && quiz_data.questions[selected_question].type !== QuizQuestionType.SLIDE && question_results !== null}
		{#if question_results === undefined}
			{#if !final_results_clicked}
				<div class="w-full flex justify-center">
					<h1 class="text-3xl text-white">{$t('admin_page.no_answers')}</h1>
				</div>
			{/if}
		{:else if quiz_data.questions[selected_question].type === QuizQuestionType.VOTING}
			{#await import('$lib/play/admin/voting_results.svelte')}
				<Spinner />
			{:then c}
				<svelte:component
					this={c.default}
					bind:data={question_results}
					bind:question={quiz_data.questions[selected_question]}
				/>
			{/await}
		{:else}
			{#await import('$lib/play/admin/results.svelte')}
				<Spinner />
			{:then c}
				<svelte:component
					this={c.default}
					bind:data={player_scores}
					question={quiz_data.questions[selected_question]}
					bind:new_data={question_results}
				/>
			{/await}
		{/if}
	{/if}
	<br />
	{#if get_question_title(selected_question + 1, quiz_data) === '' && selected_question + 1 === 0}
		<div class="flex flex-col justify-center w-screen h-full">
			<h1 class="text-7xl text-center text-title">{@html quiz_data.title}</h1>
			<p class="text-3xl pt-8 text-center text-title">{@html quiz_data.description}</p>
			{#if quiz_data.cover_image}
				<div class="flex justify-center align-middle items-center">
					<div class="h-[30vh] m-auto w-auto mt-12">
						{#if contentType?.startsWith('image')}
							<img
								class="max-h-full max-w-full block"
								src={`/api/v1/storage/download/${quiz_data.cover_image}`}
								alt="Not provided"
							/>
						{:else if contentType?.startsWith('video')}
							<!-- svelte-ignore a11y-media-has-caption -->
							<video
								class="max-h-full max-w-full block"
								src={getVideoUrl(`/api/v1/storage/download/${quiz_data.cover_image}`)}
								controls
								autoplay={false}
								loop={false}
							>
								Your browser does not support the video tag.
							</video>
						{:else if contentType?.startsWith('audio')}
							<!-- svelte-ignore a11y-media-has-caption -->
							<video
								class="max-h-full max-w-full block"
								src={getAudioUrl(`/api/v1/storage/download/${quiz_data.cover_image}`)}
								controls
								autoplay={false}
								loop={false}
							>
								Your browser does not support the video tag.
							</video>
						{:else}
							<p>Unsupported media type</p>
						{/if}
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>
