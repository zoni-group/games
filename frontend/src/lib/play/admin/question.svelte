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

<div class="flex justify-center " >
	<div class="flex flex-col justify-center items-center sm:w-2/3  h-1/6 p-0 mb-2 px-3">
		<div class="bg-white shadow-[#003FA7]/50 shadow-md border-[#003FA7] dark:shadow-none flex flex-col items-center border-[#003FA7] border-2 justify-center rounded-3xl w-[90vw] w-full pb-5" >
			<div class="m-auto bg-white lg:-mt-16 -mt-9 rounded-full p-3">
				<CircularTimer
					bind:text={timer_res}
					bind:progress={circular_progress}
					color="#ef4444"
				/>
			</div>
			<h1 class="lg:text-3xl text-base  text-center text-[#00529B]">
				{@html quiz_data.questions[selected_question].question}
			</h1>
		</div>
	</div>

</div>
<div class="lg:flex-col flex mt-8 p-5 items-center">
	{#if quiz_data.questions[selected_question].image !== null}
		<div class="flex justify-center w-1/3 lg:w-full p-0">
			<MediaComponent
				src={quiz_data.questions[selected_question].image}
				muted={false}
				css_classes="max-h-[50vh] object-cover mx-auto mb-8 w-auto"
			/>
		</div>
	{/if}
	{#if quiz_data.questions[selected_question].type === QuizQuestionType.ABCD || quiz_data.questions[selected_question].type === QuizQuestionType.VOTING || quiz_data.questions[selected_question].type === QuizQuestionType.CHECK}
		<div class="grid grid-rows-2 grid-flow-col auto-cols-auto gap-2 w-4/5 lg:w-full ps-1 ">
			{#each quiz_data.questions[selected_question].answers as answer, i}
				<div
					class="rounded-lg h-full flex border-2 border-[#0056BD] items-center flex-grow lg:min-h-[7vh] lg:min-w-full lg:max-h-[20vh] lg:max-w-[48vw] w-[30vw] transition-all"
					style="background-color: {answer.color ?? default_colors[i]};"
					class:opacity-50={!answer.right &&
						timer_res === '0' &&
						quiz_data.questions[selected_question].type === QuizQuestionType.ABCD}
				>
					<p class="md:text-7xl text-4xl font-bold text-[#fff] ps-1">
						{optionsLabel[i]}
					</p>
					<p
						class="text-center fluid-text-md lg:text-2xl break-all md:text-xl sm:text-lg px-2 overflow-auto py-2 w-full text-[#fff] "
						>{answer.answer}</p
					>
				</div>
			{/each}
		</div>
	{:else if quiz_data.questions[selected_question].type === QuizQuestionType.TEXT}
		{#if timer_res === '0'}
			<div class="grid grid-cols-2 grid-flow-col auto-cols-auto gap-2 w-4/5 lg:w-full ps-1 ">
				{#each quiz_data.questions[selected_question].answers as answer, i}
					<div class="rounded-lg h-full flex border-2 border-[#0056BD] items-center flex-grow lg:min-h-[7vh] lg:w-[48vw] lg:max-h-[20vh] lg:max-w-[48vw] w-[30vw] transition-all" style="background-color: {answer.color ??
										default_colors[i]};">
						<span class="text-center fluid-text-md lg:text-2xl break-all md:text-xl sm:text-lg px-2 overflow-auto py-2 w-full text-[#fff] "
						style="color: {get_foreground_color(
												answer.color ?? default_colors[i]
											)}"
							>{answer.answer}</span
						>
					</div>
				{/each}
			</div>
		{:else}
			<div class="flex justify-center text-white">
				<p class="fluid-text-md text-[#00529B] dark:text-white">{$t('admin_page.enter_answer_into_field')}</p>
			</div>
		{/if}
	{/if}
</div>
