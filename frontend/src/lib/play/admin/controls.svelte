<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { QuizQuestionType } from '$lib/quiz_types';
	import type { QuizData } from '$lib/quiz_types';
	import type { Socket } from 'socket.io-client';
	import { getLocalization } from '$lib/i18n';

	import { toast } from '@zerodevx/svelte-toast';
	import { fade } from 'svelte/transition';
	export let bg_color: string;
	export let selected_question: number;
	export let quiz_data: QuizData;
	export let timer_res: string;
	export let final_results;
	export let socket: Socket;
	export let answer_count: number;
	export let game_token: string;
	export let game_pin: string;
	export let question_results;

	export let shown_question_now: number;
	let fullscreen_open = false;
	const { t } = getLocalization();
	const set_question_number = (q_number: number) => {
		socket.emit('set_question_number', q_number.toString());
	};

	const get_question_results = () => {
		socket.emit('get_question_results', {
			game_id: game_token,
			question_number: shown_question_now
		});
	};
	const show_solutions = () => {
		socket.emit('show_solutions', {});
		timer_res = '0';
	};

	const get_final_results = () => {
		socket.emit('get_final_results', {});
	};

	socket.on('set_question_number', ({ question_index }) => {
		selected_question = question_index;
	});

	socket.on('start_game', () => {
		set_question_number(0);
	});
	const copyUrl = () => {
		const url = `https://${window.location.host}/play?pin=${game_pin}`;
		navigator.clipboard.writeText(url).then(() => {
			toast.push('URL copied to clipboard! Share it!');
		});
	};
</script>

<div
	class="  w-full h-10 mt-4 px-4 z-20 grid grid-cols-2"
	style="background: {bg_color ? bg_color : 'transparent'}"
	class:text-black={bg_color}
>
	<p
		class="fixed top-20 left-10 z-40 text-xs sm:text-base mr-auto ml-0 col-start-1 col-end-1 flex items-center italic justify-center font-semibold bg-[#003FA7] text-white dark:text-white rounded-full sm:w-[10vw] w-12 h-12 md:w-20 md:h-20 border-8 border-[#fff] sm:h-[10vw]"
	>
		{selected_question === -1 ? '0' : selected_question + 1}
		/ {quiz_data.questions.length}
	</p>
	<div class="fixed top-10 right-0 px-4 z-40 flex flex-col items-center space-y-4">
		{#if selected_question + 1 === quiz_data.questions.length && ((timer_res === '0' && question_results !== null) || quiz_data?.questions?.[selected_question]?.type === QuizQuestionType.SLIDE)}
			{#if JSON.stringify(final_results) === JSON.stringify([null])}
				<button on:click={get_final_results} class="slide-control-btn">
					{$t('admin_page.get_final_results')}
				</button>
			{/if}
		{:else if timer_res === '0' || selected_question === -1}
			{#if (selected_question + 1 !== quiz_data.questions.length && question_results !== null) || selected_question === -1}
				<button
					on:click={() => set_question_number(selected_question + 1)}
					class="slide-control-btn"
				>
					{$t('admin_page.next_question', { question: selected_question + 2 })}
				</button>
			{/if}
			{#if question_results === null && selected_question !== -1}
				{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
					<button
						on:click={() => set_question_number(selected_question + 1)}
						class="slide-control-btn"
					>
						{$t('admin_page.next_question', { question: selected_question + 2 })}
					</button>
				{:else}
					<button on:click={get_question_results} class="slide-control-btn">
						{$t('admin_page.show_results')}
					</button>
				{/if}
			{/if}
		{:else if selected_question !== -1}
			{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
				<button
					on:click={() => set_question_number(selected_question + 1)}
					class="slide-control-btn"
				>
					{$t('admin_page.next_question', { question: selected_question + 2 })}
				</button>
			{:else}
				<button on:click={show_solutions} class="slide-control-btn">
					{$t('admin_page.stop_time_and_solutions')}
				</button>
			{/if}
		{/if}
		<div
			class="fixed right-0 top-20 lg:text-sm text-xs px-4 py-2 mr-3 mt-4 rounded-xl text-white bg-black bg-opacity-20 shadow-lg"
		>
			{$t('admin_page.answers_submitted', { answer_count: answer_count })}
		</div>
		{#if selected_question + 1 != quiz_data.questions.length}
			<div
				class="fixed right-0 top-32 lg:text-sm text-xs px-4 py-2 mr-3 mt-4 rounded-xl  text-white  "
			>
				<div class="flex flex-col justify-center items-center border-2 dark:bg-transparent bg-[#FFFFFF] border-[#9E9E9E] py-1 rounded-3xl shadow-lg">
					
					<div class=" flex flex-col justify-center items-center w-full p-3">
						<!-- svelte-ignore a11y-click-events-have-key-events -->
						<div class=" rounded-xl flex flex-col justify-center rounded-xl bg-[#FFFFFF] dark:bg-[#BFBFBF]">
							<img
								on:click={() => (fullscreen_open = true)}
								alt={$t('qr_code_to_join_the_game')}
								src={`/api/v1/utils/qr/${game_pin}`}
								class=" bg-[#FFFFF] "
								width="150"
								height="150"
							/>
						</div>
					</div>
					<p class="text-[1.2rem] font-bold text-[#0056BD] dark:text-white" >Join: </p>
					<div class="flex justify-center items-center mt-2 gap-2" >
						<p
							on:click={copyUrl}
							class="underline cursor-pointer text-[#0056BD] dark:text-white text-[1.2rem] font-bold w-fit  rounded-xl"
						>
							ai.zoni.edu
						</p>
					</div>
					<div class="flex justify-center items-center my-2 gap-2" >
						<p class="text-[1.2rem] font-bold text-[#0056BD] dark:text-white" >Code: </p>
						<p class="  text-[#0056BD] dark:text-white text-[1.2rem] font-bold w-fit  text-[#0056BD] dark:text-white rounded-xl" >
							{game_pin}
						</p>
					</div>
				</div>
			</div>
		{/if}
	</div>
	{#if fullscreen_open}
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<div
			class="fixed top-0 left-0 z-50 w-screen min-h-screen bg-black bg-opacity-50 flex p-2"
			transition:fade={{ duration: 80 }}
			on:click={() => (fullscreen_open = false)}
		>
			<img
				alt={$t('qr_code_to_join_the_game')}
				src={`/api/v1/utils/qr/${game_pin}`}
				class="object-contain rounded m-auto md:w-1/2 w-full bg-white"
			/>
		</div>
	{/if}
</div>

<style>
	.slide-control-btn {
		@apply bg-[#003FA7] text-white font-semibold py-2 px-4 rounded-lg shadow-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75;
	}
</style>
