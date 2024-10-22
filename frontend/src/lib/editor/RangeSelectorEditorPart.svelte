<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData } from '../quiz_types';
	import Spinner from '../Spinner.svelte';

	export let selected_question: number;
	export let data: EditorData;

	let question = data.questions[selected_question];
	if (question.answers.max === undefined || question.answers.min_correct === undefined) {
		question.answers = {
			max: 10,
			min: 0,
			max_correct: 7,
			min_correct: 3
		};
	}

	/*
	const correct_numbers = (data: number[]) => {
		console.log(data, data[1] <= data[0])
		if (data[1] <= data[0]) {
			range_arr[1] = range_arr[0] + 2
		}
		if (data[0] <= data[1]) {
			range_arr[0] = range_arr[1] - 2
		}
	}
	$: correct_numbers(range_arr)

 */
	let answer = question.answers;
	let range_arr = [answer.min_correct, answer.max_correct];
	$: data.questions[selected_question].answers.min_correct = range_arr[0];
	$: data.questions[selected_question].answers.max_correct = range_arr[1];
	$: data.questions[selected_question].answers.min =
		data.questions[selected_question].answers.min === null
			? 0
			: data.questions[selected_question].answers.min;
	$: data.questions[selected_question].answers.max =
		data.questions[selected_question].answers.max === null
			? 0
			: data.questions[selected_question].answers.max;

	function sleep(ms) {
		return new Promise((resolve) => setTimeout(resolve, ms));
	}
</script>

<div class="w-full mx-8">
	<div class="flex justify-center">
		<div class="grid grid-cols-2 gap-4">
			<input
				type="number"
				class="w-16 bg-transparent rounded-lg text-lg border-2 border-gray-500 p-1"
				max={data.questions[selected_question].answers.max - 2}
				bind:value={data.questions[selected_question].answers.min}
			/>
			<input
				type="number"
				class="w-16 bg-transparent rounded-lg text-lg border-2 border-gray-500 p-1"
				min={data.questions[selected_question].answers.min + 2}
				bind:value={data.questions[selected_question].answers.max}
			/>
		</div>
	</div>
	<div class="w-full">
		<!--		<RangeSlider bind:value={range_arr} bind:min={answer.min} bind:max={answer.max} range={true} slider={lol} /> -->

		{#await import('svelte-range-slider-pips')}
			<Spinner my_20={false} />
		{:then c}
			{#await sleep(100)}
				<Spinner my_20={false} />
			{:then _}
				<svelte:component
					this={c.default}
					bind:values={range_arr}
					bind:min={data.questions[selected_question].answers.min}
					bind:max={data.questions[selected_question].answers.max}
					pips
					float
					all="label"
					range
				/>
			{/await}
		{/await}
	</div>
</div>
<style>
	:root {
	  --range-slider:            hsl(0, 17.2%, 46.9%);
	  --range-handle-inactive:   hsl(358.6, 84.7%, 59%);
	  --range-handle:            hsl(358.6, 84.7%, 59%);
	  --range-handle-focus:      hsl(358.6, 84.7%, 59%);
	  --range-handle-border:     hsl(0, 80%, 2%);
	  --range-range-inactive:    hsl(208.3, 100%, 30.4%);
	  --range-range:             hsl(208.3, 100%, 30.4%);
	  --range-float-inactive:    hsl(208.3, 100%, 30.4%);
	  --range-float:             hsl(358.6, 84.7%, 59%);
	  --range-float-text:        hsl(0, 0%, 85.9%);
  
	  --range-pip:               hsl(0, 0%, 98%);
	  --range-pip-text:          hsl(0, 0%, 72.2%);
	  --range-pip-active:        hsl(214, 100%, 37.1%);
	  --range-pip-active-text:   hsl(209.2, 100%, 37.1%);
	  --range-pip-hover:         hsl(214, 100%, 46.1%);
	  --range-pip-hover-text:    hsl(209.2, 100%, 35.1%);
	  --range-pip-in-range:      hsl(206, 100%, 33.9%);
	  --range-pip-in-range-text: hsl(214, 100%, 38%);
	}
  </style>