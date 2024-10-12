<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { QuizQuestionType } from '$lib/quiz_types';
	import type { QuizData } from '$lib/quiz_types';
	import { get_foreground_color } from '$lib/helpers.js';
	import { kahoot_icons } from '$lib/play/kahoot_mode_assets/kahoot_icons.js';
	import CircularTimer from '$lib/play/circular_progress.svelte';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import { getLocalization } from '$lib/i18n';

	export let quiz_data: QuizData;
	export let selected_question: number;
	export let timer_res: string;

	export let answer_count: number;
	export let default_colors: string[];
	let optionsLabel = ["A","B","C","D"];
	const { t } = getLocalization();

	let circular_progress = 0;
	$: {
		try {
			circular_progress =
				1 -
				((100 / parseInt(quiz_data.questions[selected_question].time)) *
					parseInt(timer_res)) /
					100;
		} catch {
			circular_progress = 0;
		}
	}
</script>
<style>
	 .fluid-text {
    font-size: clamp(0.5rem, 0.5vw + 0.5rem, 0.5rem);
  }
  @media (min-width: 1080px){
	.fluid-text {
    font-size: 1.25rem;
  }
  }
</style>

<div class="flex justify-center mt-[135px] sm:mt-0">
	<div class="flex flex-col justify-center items-center sm:w-2/3 h-1/6 p-0 mb-1 px-3 mt-1">
		<div class="bg-white shadow-[#003FA7]/50 shadow-md border-[#003FA7] dark:shadow-none flex flex-col items-center border-[#003FA7] border-2 justify-center rounded-3xl w-[90vw] w-full pb-2">
			<div class="m-auto bg-white lg:-mt-10 -mt-6 rounded-full p-1">
				<CircularTimer
					bind:text={timer_res}
					bind:progress={circular_progress}
					color="#ef4444"
				/>
			</div>
			<!-- Question Text -->
			<div class="flex-shrink-0 p-4">
				<h1 class="text-center text-[#00529B]"
					style="font-size: clamp(1rem, 3vw + 1vh, 4vh);">
					{@html quiz_data.questions[selected_question].question}
				</h1>
			</div>
			{#if quiz_data.questions[selected_question].image !== null}
			<div class="flex justify-center w-full p-0">
					<MediaComponent
						src={quiz_data.questions[selected_question].image}
						muted={false}
						css_classes="max-h-[35vh] object-cover mx-auto mb-0 w-auto"
					/>
			</div>
			{/if}
		</div>
	</div>
	

</div>
<div class="flex flex-col flex-row mt-0 p-0 items-center">
	{#if quiz_data.questions[selected_question].type === QuizQuestionType.ABCD ||
		quiz_data.questions[selected_question].type === QuizQuestionType.VOTING ||
		quiz_data.questions[selected_question].type === QuizQuestionType.CHECK}
	<!-- Main Container -->
	<div class="flex flex-col h-1/2">
		<!-- Answers Grid -->
		<div class="flex-grow flex items-center justify-center">
		<div class="grid grid-rows-2 gap-2 w-full h-full max-h-[45vh] min-w-[30vh] grid-flow-col auto-cols-auto p-4">
			{#each quiz_data.questions[selected_question].answers as answer, i}
			<div
				class="rounded-lg flex border-2 border-[#0056BD] items-center justify-center p-2 transition-all"
				style="
				background-color: {answer.color ?? default_colors[i]};
				"
				class:opacity-50={!answer.right && timer_res === '0' &&
				quiz_data.questions[selected_question].type === QuizQuestionType.ABCD}>
				{#if quiz_data.questions[selected_question].ansType === "TEXT" ||
					quiz_data.questions[selected_question].ansType === null}
				<p class="font-bold text-[#fff] ps-1"
					style="font-size: clamp(2rem, 4vh, 8vh);">
					{optionsLabel[i]}
				</p>
				<p class="text-center break-all px-2 py-2 w-full text-[#fff]"
					style="font-size: clamp(1rem, 2vh, 4vh);">
					{answer.answer}
				</p>
				{:else}
				<MediaComponent
					css_classes="w-full h-full object-contain max-h-[25vh]"
					bind:src={answer.answer} />
				{/if}
			</div>
			{/each}
		</div>
		</div>
	</div>
	{:else if quiz_data.questions[selected_question].type === QuizQuestionType.TEXT}
	<!-- Main Container -->
	<div class="flex flex-col h-1/2">
		<!-- Answer Input or Display -->
		{#if timer_res === '0'}
		<!-- Display Answers After Timer Ends -->
		<div class="flex-grow flex items-center justify-center">
			<div class="grid grid-rows-2 gap-2 w-full h-full max-h-[45vh] min-w-[30vh] grid-flow-col auto-cols-auto p-4">
			{#each quiz_data.questions[selected_question].answers as answer, i}
				<div class="rounded-lg flex items-center justify-center border-2 border-[#0056BD] transition-all"
					style="background-color: {answer.color ?? default_colors[i]};">
				<span class="text-center text-[#fff]"
						style="font-size: clamp(1rem, 2vh, 4vh);">
					{answer.answer}
				</span>
				</div>
			{/each}
			</div>
		</div>
		{:else}
		<!-- Input Field -->
		<div class="flex-grow flex items-center justify-center h-full">
			<p class="text-center text-[#00529B] dark:text-white"
			style="font-size: clamp(1rem, 2vh, 4vh);">
			{$t('admin_page.enter_answer_into_field')}
			</p>
		</div>
		{/if}
	</div>
	{/if}
</div>
