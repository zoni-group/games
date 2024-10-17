<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { OrderQuizAnswer, Question } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { fade, fly } from 'svelte/transition';
	import { getLocalization } from '$lib/i18n';
	import Spinner from '$lib/Spinner.svelte';
	import { flip } from 'svelte/animate';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import { get_foreground_color } from '../helpers';
	import { dndzone, SHADOW_ITEM_MARKER_PROPERTY_NAME } from 'svelte-dnd-action';
	import { cubicIn } from 'svelte/easing';
	import RightArrow from '$lib/icons/rightArrow.svelte';

	export let question: Question;

	const { t } = getLocalization();
	const flipDurationMs = 200;

	let selected_answer = undefined;
	let timer_res = question.time;
	let show_results = false;

	// Stop the timer if the question is answered
	const timer = (time: string) => {
		let seconds = Number(time);
		let timer_interval = setInterval(() => {
			if (timer_res === '0') {
				clearInterval(timer_interval);

				return;
			} else {
				seconds--;
			}

			timer_res = seconds.toString();
		}, 1000);
	};
	let slider_value = [0];
	if (question.type === QuizQuestionType.RANGE) {
		slider_value[0] = (question.answers.max - question.answers.min) / 2 + question.answers.min;
	}
	let slider_values = [question.answers.min_correct ?? 0, question.answers.max_correct ?? 0];
	let items = Array.isArray(question.answers) ? question.answers.map((answer, index) => ({
        id: index, 
        answer, 
        color: answer.color
	})) : [];
	$: {
		items = Array.isArray(question.answers) ? question.answers.map((answer, index) => ({
			id: index, 
			answer, 
			color: answer.color
		})) : [];
	}
	$: console.log(items, "moIn!", question.answers);
	
	function handleSort(e) {
        items = e.detail.items;
    }
	let text_input;
	timer(question.time);

	let check_choice_selected = [false, false, false, false];

	function shuffleArray(a) {
		for (let i = a.length - 1; i > 0; i--) {
			const j = Math.floor(Math.random() * (i + 1));
			[a[i], a[j]] = [a[j], a[i]];
		}
		return a;
	}

	const swapArrayElements = (arr, a: number, b: number) => {
		let _arr = [...arr];
		let temp = _arr[a];
		_arr[a] = _arr[b];
		_arr[b] = temp;
		return _arr;
	};

	let original_order: OrderQuizAnswer[] = [];

	if (question.type === QuizQuestionType.ORDER) {
		for (let i = 0; i < question.answers.length; i++) {
			question.answers[i] = { answer: question.answers[i].answer, id: i };
		}
		original_order = [...question.answers];
		console.log(original_order);
		shuffleArray(question.answers);
	}

	let order_corrected = false;
	const select_complex_answer = () => {
		/*		const correct_order_ids = []
                for (const e of original_order) {
                    correct_order_ids.push(e.id)
                }
                const user_set_ids = []
                for (const e of answer) {
                    correct_order_ids.push(e.id)
                }*/
		question.answers = original_order;
		order_corrected = true;
		timer_res = '0';
	};

	const default_colors = ['#FFA800', '#00A3FF', '#FF1D38', '#00D749'];


	// Function to determine if the color is light or dark
	function isColorLight(color) {
		const hex = color.replace('#', '');
		const r = parseInt(hex.substring(0, 2), 16);
		const g = parseInt(hex.substring(2, 4), 16);
		const b = parseInt(hex.substring(4, 6), 16);
		const brightness = (r * 299 + g * 587 + b * 114) / 1000;
		return brightness > 155; // higher value means the color is light
	}
	
	// Function to get the appropriate text color
	function getTextColor(backgroundColor) {
		return isColorLight(backgroundColor) ? 'black' : 'white';
	}
</script>

<div class="w-full px-6 lg:px-20 h-[80vh] absolute" in:fly={{ x: 100 }} out:fly={{ x: -100 }}>
	<h1 class="lg:text-2xl text-lg text-center text-[#0056BD] dark:text-white mt-2 break-normal mb-2 mt-20">
		{@html question.question}
	</h1>
	{#if question.image !== null}
		<div>
			<MediaComponent
				src={question.image}
				css_classes="max-h-[40vh] object-cover mx-auto mb-8 w-auto"
			/>
		</div>
	{/if}
	<p class="text-center text-[#0056BD] dark:text-white">{timer_res}</p>
	{#if question.type === QuizQuestionType.ABCD}
		{#if show_results}
			<div class='grid grid-rows-2 gap-2 w-full grid-cols-2'>
				{#each question.answers as answer, i}
					<button
						disabled
						class:bg-green-500={question.answers[i].right}
						class:bg-red-500={!question.answers[i].right}
						class:text-xl={i === selected_answer}
						class:underline={i === selected_answer}
						class="rounded-lg h-full  flex items-center justify-center disabled:opacity-60 border-4 border-white transition-all my-2"
					>
					{#if question.ansType === 'IMAGE'}
						<MediaComponent 
							css_classes="inline-block m-auto max-h-[30vh]" 
							src={answer.answer}
							allow_fullscreen={false}
						/>
					{:else}
						<p class="m-auto button-text text-sm text-[{getTextColor(answer.color ?? '#fff')}] dark:text-[{getTextColor(answer.color ?? '#fff')}] sm:text-base md:text-lg lg:text-xl">{answer.answer}</p>
					{/if}
					</button
					>
				{/each}
			</div>
		{:else}
			<div class='grid grid-rows-2 gap-2 w-full grid-cols-2'>
				{#each question.answers as answer, i}
					<button
						disabled={selected_answer !== undefined || timer_res === '0'}
						type="button"
						class="rounded-lg h-full  flex items-center justify-center disabled:opacity-60 border-4 border-white transition-all my-2 disabled:grayscale text-black"
						style="background-color: {answer.color ?? default_colors[i]}; color: {get_foreground_color(answer.color ?? default_colors[i])}"
						class:disabled:opacity-60={selected_answer !== i}
						class:disabled:grayscale={selected_answer !== i}
						on:click={() => {
							selected_answer = i;
							timer_res = '0';
						}}>
						{#if question.ansType === 'IMAGE'}
							<MediaComponent 
								css_classes="inline-block m-auto max-h-[30vh]" 
								src={answer.answer}
								allow_fullscreen={false}
							/>
						{:else}
							<p class="m-auto button-text text-sm text-[{getTextColor(answer.color ?? '#fff')}] dark:text-[{getTextColor(answer.color ?? '#fff')}] sm:text-base md:text-lg lg:text-xl">{answer.answer}</p>
						{/if}
					</button
					>
				{/each}
			</div>
			{#if timer_res === '0'}
				<div class="relative z-10 flex justify-center">
					<button
						class="bg-orange-500 p-2 rounded-lg flex justify-center w-1/2 max-w-xs transition my-5 text-black"
						type="button"
						on:click={() => {
							show_results = true;
						}}>{$t('admin_page.get_results')}</button>
				</div>
			{/if}			
		{/if}
	{:else if question.type === QuizQuestionType.RANGE}
		{#if timer_res === '0'}
			{#await import('svelte-range-slider-pips')}
				<Spinner />
			{:then c}
				<div class="grayscale pointer-events-none w-full">
					<svelte:component
						this={c.default}
						bind:values={slider_values}
						bind:min={question.answers.min}
						bind:max={question.answers.max}
						pips
						float
						all="label"
					/>
				</div>
			{/await}
		{:else}
			{#await import('svelte-range-slider-pips')}
				<Spinner />
			{:then c}
				<div class:pointer-events-none={selected_answer !== undefined}>
					<svelte:component
						this={c.default}
						bind:values={slider_value}
						bind:min={question.answers.min}
						bind:max={question.answers.max}
						pips
						float
						all="label"
					/>
				</div>
				<div class="flex justify-center">
					<button
						type="button"
						class="w-1/3 text-3xl bg-[#004A93] my-2 disabled:opacity-60 rounded-lg p-1 transition"
						disabled={selected_answer !== undefined}
						on:click={() => {
							selected_answer = slider_value[0];
							timer_res = '0';
						}}
						>{$t('words.submit')}
					</button>
				</div>
			{/await}
		{/if}
	{:else if question.type === QuizQuestionType.VOTING}
		<div class='grid grid-rows-2 gap-2 w-full grid-cols-2'>
			{#each question.answers as answer, i}
				<button
					type="button"
					disabled={selected_answer !== undefined || timer_res === '0'}
					class="rounded-lg h-full  flex items-center justify-center border-4 border-white transition-all my-2 text-black"
					style="background-color: {answer.color ?? default_colors[i]}; color: {get_foreground_color(answer.color ?? default_colors[i])}"
					class:disabled:opacity-60={selected_answer !== i}
					class:disabled:grayscale={selected_answer !== i}
					on:click={() => {
						selected_answer = i;
						timer_res = '0';
					}}>
					{#if question.ansType === 'IMAGE'}
						<MediaComponent 
							css_classes="inline-block m-auto max-h-[30vh]" 
							src={answer.answer}
							allow_fullscreen={false}
						/>
					{:else}
						<p class="m-auto button-text text-sm text-[{getTextColor(answer.color ?? '#fff')}] dark:text-[{getTextColor(answer.color ?? '#fff')}] sm:text-base md:text-lg lg:text-xl">{answer.answer}</p>
					{/if}
				</button>
			{/each}
		</div>
		{#if timer_res === '0'}
			<p class="text-center text-[#0056BD] dark:text-white">No correct answers, since this is a poll-question</p>
		{/if}
	{:else if question.type === QuizQuestionType.SLIDE}
		{#await import('$lib/play/admin/slide.svelte')}
			<Spinner my={false} />
		{:then c}
			<div class="max-h-[90%] max-w-[90%]">
				<svelte:component this={c.default} bind:question />
			</div>
		{/await}
	{:else if question.type === QuizQuestionType.TEXT}
		{#if timer_res === '0'}
			{#each question.answers as answer, i}
				<div
					class="p-2 rounded-lg flex justify-center w-full transition bg-gray-200 my-5 text-black"
				>
					{answer.answer}
				</div>
			{/each}
		{:else}
			<div class="flex justify-center mt-2">
				<input
					type="text"
					bind:value={text_input}
					class="bg-gray-50 focus:ring text-gray-900 rounded-lg focus:ring-blue-500 block w-full p-2 dark:bg-gray-700 dark:text-white dark:focus:ring-blue-500 outline-none transition text-center"
				/>
			</div>
			<div class="flex justify-center">
				<button
					type="button"
					disabled={!text_input}
					class="w-1/3 text-3xl bg-[#004A93] my-2 disabled:opacity-60 rounded-lg p-1 transition"
					on:click={() => {
						selected_answer = text_input;
						timer_res = '0';
					}}>{$t('words.submit')}</button
				>
			</div>
		{/if}
	{:else if question.type === QuizQuestionType.ORDER}
	<div class="flex flex-col justify-center items-center w-full" >
		<section 
			use:dndzone={{items, flipDurationMs, dropTargetStyle:{"outline": "none"} ,dropTargetClasses: ["py-4","border-0","dark:bg-[#0AEDFE]/30","shadow-lg", "outline-none","rounded-lg","dark:shadow-black","shadow-black/40","transition-all","ease-in-out", "bg-[#E9F3FF]"]}} 
			on:consider={handleSort} 
			on:finalize={handleSort}
			class="flex flex-col justify-center items-center md:w-3/4 w-full gap-4 px-4 "
			style="overflow-y: auto; -webkit-overflow-scrolling: touch;"
		>
			{#each items as item (item.id)}
				<div 
					class="w-4/5 h-fit flex-row rounded-lg p-1 align-middle relative"
					animate:flip={{ duration: flipDurationMs }}
					style="color: {getTextColor(item.color ?? '#004A93')}; background-color: {item.color ?? '#004A93'};"
				>
					<p class="w-full text-center p-1 text-2xl text-white">
						{item.answer.answer}
					</p>
					{#if item[SHADOW_ITEM_MARKER_PROPERTY_NAME]}
						<div in:fade={{duration:200, easing: cubicIn}} class='custom-shadow-item w-full h-full flex-row rounded-lg p-1 align-middle opacity-10' style="color: {getTextColor(item.color ?? '#004A93')}; ">
							<p class="w-full text-center p-1 text-2xl text-white">
								{item.answer.answer}
							</p>
						</div>
					{/if}
				</div>
			{/each}
		</section>	
		<div class="w-full flex justify-center mt-4">
			<button 
				type="button"
				class="bg-[#0056BD] border-[#fff] flex items-center border-2 gap-2 text-[#fff] font-semibold px-9 py-2 rounded-full disabled:cursor-not-allowed disabled:opacity-90"
				on:click={() => select_complex_answer()}
				disabled={true}
			>
				<RightArrow />
				Submit
			</button>
		</div>
	</div>
	{:else if question.type === QuizQuestionType.CHECK}
		{#if show_results}
			<div class='grid grid-rows-2 gap-2 w-full grid-cols-2'>
				{#each question.answers as answer, i}
					<button
						disabled
						class:bg-green-500={question.answers[i].right}
						class:bg-red-500={!question.answers[i].right}
						class:text-xl={i === selected_answer}
						class:underline={i === selected_answer}
						class="rounded-lg h-full  flex items-center justify-center border-4 border-white transition-all my-2"
						class:opacity-60={!question.answers[i].right}
					>
					{#if question.ansType === 'IMAGE'}
						<MediaComponent 
							css_classes="inline-block m-auto max-h-[30vh]" 
							src={answer.answer}
							allow_fullscreen={false}
						/>
					{:else}
						<p class="m-auto button-text text-sm text-[{getTextColor(answer.color ?? '#fff')}] dark:text-[{getTextColor(answer.color ?? '#fff')}] sm:text-base md:text-lg lg:text-xl">{answer.answer}</p>
					{/if}
					</button
					>
				{/each}
			</div>
		{:else}
			<div class="grid grid-rows-2 gap-2 w-full grid-cols-2">
				{#each question.answers as answer, i}
					<button
						type="button"
						disabled={selected_answer !== undefined || timer_res === '0'}
						class="rounded-lg h-full w-9/10 flex items-center justify-center border-2 border-black transition-all my-2"
						style="background-color: {answer.color ?? default_colors[i]}; color: {get_foreground_color(answer.color ?? default_colors[i])}"
						class:opacity-60={!check_choice_selected[i]}
						class:disabled:opacity-60={!check_choice_selected[i]}
						class:disabled:grayscale={!check_choice_selected[i]}
						on:click={() => {
							check_choice_selected[i] = !check_choice_selected[i];
						}}>
						{#if question.ansType === 'IMAGE'}
							<MediaComponent 
								css_classes="inline-block m-auto max-h-[30vh]" 
								src={answer.answer}
								allow_fullscreen={false}
							/>
						{:else}
							{answer.answer}
						{/if}
					</button>
				{/each}
			</div>
			<div class="relative z-10 flex justify-center items-center w-1/2 max-w-xs mt-5 mx-auto">
				{#if timer_res !== '0'}
				<BrownButton
					type="button"
					on:click={() => {
						selected_answer = check_choice_selected;
						timer_res = '0';
					}}>{$t('words.submit')}</BrownButton
				>
				{/if}
				{#if timer_res === '0'}
					<button
						type="button"
						class="bg-orange-500 p-2 rounded-lg flex justify-center w-1/2 max-w-xs transition my-5 text-black"
						on:click={() => {
							show_results = true;
						}}>{$t('admin_page.get_results')}</button
					>
				{/if}
			</div>
		{/if}
	{/if}
</div>
<style>
	.custom-shadow-item {
		position: absolute;
		top: 0; left:0; right: 0; bottom: 0;
		visibility: visible;
		border: 1px dashed grey;
		background: lightblue;
		opacity: 0.5;
		margin: 0;
	}
</style>