<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { QuizQuestionType } from '$lib/quiz_types';
	import type { QuizData } from '$lib/quiz_types';
	import type { Socket } from 'socket.io-client';
	import { getLocalization } from '$lib/i18n';

	export let bg_color: string;
	export let selected_question: number;
	export let quiz_data: QuizData;
	export let timer_res: string;
	export let final_results;
	export let socket: Socket;
	export let answer_count: number;
	export let game_token: string;

	export let question_results;

	export let shown_question_now: number;

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
</script>
<style>
	.slide-control-btn {
	  @apply bg-blue-500 text-white font-semibold py-2 px-4 rounded-lg shadow-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75;
	}
  </style>
<div
	class="  w-full h-10 mt-4 px-4 z-20 grid grid-cols-2"
	style="background: {bg_color ? bg_color : 'transparent'}"
	class:text-black={bg_color}
>
	<p class="fixed top-10 left-10 z-50 mr-auto ml-0 col-start-1 col-end-1 flex items-center italic justify-center font-semibold bg-white text-black dark:text-black rounded-full w-20 border-8 border-[#0AEDFE] h-20">
		{selected_question === -1 ? '0' : selected_question + 1}
		/ {quiz_data.questions.length}
	</p>
	<div class="fixed top-4 right-20 z-50 flex flex-col items-center space-y-4">
		{#if selected_question + 1 === quiz_data.questions.length && ((timer_res === '0' && question_results !== null) || quiz_data?.questions?.[selected_question]?.type === QuizQuestionType.SLIDE)}
		  {#if JSON.stringify(final_results) === JSON.stringify([null])}
			<button on:click={get_final_results} class="slide-control-btn">
			  {$t('admin_page.get_final_results')}
			</button>
		  {/if}
		{:else if timer_res === '0' || selected_question === -1}
		  {#if (selected_question + 1 !== quiz_data.questions.length && question_results !== null) || selected_question === -1}
			<button on:click={() => set_question_number(selected_question + 1)} class="slide-control-btn">
			  {$t('admin_page.next_question', { question: selected_question + 2 })}
			</button>
		  {/if}
		  {#if question_results === null && selected_question !== -1}
			{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
			  <button on:click={() => set_question_number(selected_question + 1)} class="slide-control-btn">
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
			<button on:click={() => set_question_number(selected_question + 1)} class="slide-control-btn">
			  {$t('admin_page.next_question', { question: selected_question + 2 })}
			</button>
		  {:else}
			<button on:click={show_solutions} class="slide-control-btn">
			  {$t('admin_page.stop_time_and_solutions')}
			</button>
		  {/if}
		{/if}
		<p class=" text-lg px-4 py-2 mx-3 mt-4 rounded-xl text-white">
			{$t('admin_page.answers_submitted', { answer_count: answer_count })}
		</p>
	  </div>
</div>
