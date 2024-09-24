<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { socket } from '$lib/socket';
	import Spinner from '../Spinner.svelte';
	import { getLocalization } from '$lib/i18n';
	import { kahoot_icons } from './kahoot_mode_assets/kahoot_icons';
	import CircularTimer from '$lib/play/circular_progress.svelte';
	import { flip } from 'svelte/animate';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { get_foreground_color } from '../helpers';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import { toast } from '@zerodevx/svelte-toast';
	import RightArrow from '$lib/icons/rightArrow.svelte';
	import en from '$lib/i18n/locales/en.json';

	const { t } = getLocalization();

	export let question: Question;
	export let game_mode;
	export let question_index: string | number;
	export let solution;
	export let language;

	$: console.log(question_index, question, 'hi!');

	console.log(question);
	
	if (question.type === undefined) {
		question.type = QuizQuestionType.ABCD;
	} else {
		question.type = QuizQuestionType[question.type];
	}

	let timer_res = question.time;
	let selected_answer: string | [] =  JSON.parse(localStorage.getItem("game_state"))?.acknowledge?.answer || undefined;
	let text_answer = [];
	let acknowledgement = JSON.parse(localStorage.getItem("game_state"))?.acknowledge?.answered || false;
	let showPlayerAnswers = acknowledgement || false;

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
	socket.on('everyone_answered', (_) => {
		timer_res = '0';
	});

	timer(question.time);

	$: {
		if (solution !== undefined) {
			timer_res = '0';
		}
	}

	const cleanAnswer = (answer: string) => {
		return answer.trim().replace(/\s+/g, ' ');
	};

	const selectAnswer = (answer: string) => {
		selected_answer = answer;
		socket.emit('submit_answer', {
			question_index: question_index,
			answer: cleanAnswer(answer)
		});
		toast.push(`You selected: ${cleanAnswer(selected_answer)}`);
	};

	socket.on('answer_acknowledged', () => {
		const val = {
			answered: true,
			answer: selected_answer,
		};
		const storeState = JSON.parse(localStorage.getItem("game_state"));
		storeState.acknowledge = val;
		localStorage.setItem("game_state", JSON.stringify(storeState));
		showPlayerAnswers = true;
	});

	const selectRangeAnswer = (answer: string) => {
		selected_answer = answer;
		socket.emit('submit_answer', {
			question_index: question_index,
			answer: answer
		});
		toast.push(`You selected: ${answer}`);
		showPlayerAnswers = true;
	};

	const selectCheckAnswer = (answer: string, text_answer: []) => {
		selected_answer = text_answer;
		socket.emit('submit_answer', {
			question_index: question_index,
			answer: answer,
		});
		toast.push(`Your answer has been submitted!`);
		showPlayerAnswers = true;
	};

	const select_complex_answer = (data) => {
		const new_array = [];
		for (let i = 0; i < data.length; i++) {
			new_array.push({ answer: data[i].answer });
		}
		selected_answer = data.map(a => a.answer);
		socket.emit('submit_answer', {
			question_index: question_index,
			answer: 'a',
			complex_answer: new_array
		});
		toast.push(`Your answer has been submitted!`);
		showPlayerAnswers = true;
	};

	let text_input = '';

	let slider_value = [0];
	if (question.type === QuizQuestionType.RANGE) {
		slider_value[0] = (question.answers.max - question.answers.min) / 2 + question.answers.min;
	}
	const set_answer_if_not_set_range = (time) => {
		if (question.type !== QuizQuestionType.RANGE) {
			return;
		}
		if (selected_answer === undefined && time === '0') {
			selected_answer = `${slider_value[0]}`;
			selectAnswer(selected_answer);
		}
	};

	if (question.type === QuizQuestionType.ORDER) {
		for (let i = 0; i < question.answers.length; i++) {
			question.answers[i] = { ...question.answers[i], id: i };
		}
	}

	const swapArrayElements = (arr, a: number, b: number) => {
		let _arr = [...arr];
		let temp = _arr[a];
		_arr[a] = _arr[b];
		_arr[b] = temp;
		return _arr;
	};
	$: set_answer_if_not_set_range(timer_res);
	let circular_progress = 0;
	$: {
		try {
			circular_progress = 1 - ((100 / question.time) * parseInt(timer_res)) / 100;
		} catch {
			circular_progress = 0;
		}
	}

	const get_div_height = (): string => {
		if (game_mode === 'normal') {
			if (question.image) {
				return '66.666667';
			} else {
				return '83.333333';
			}
		} else {
			return '100';
		}
	};
	$: console.log(slider_value, 'values');
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

	<div class={`w-screen ${game_mode !== 'normal' ? 'h-4/5 flex items-start justify-center' : 'h-full'}`}>
	{#if game_mode === 'normal'}
		<div
			class="flex flex-col justify-start"
			class:mt-10={[QuizQuestionType.RANGE, QuizQuestionType.ORDER, QuizQuestionType.TEXT]}
		>
			<h1
				class="lg:text-2xl text-lg text-center text-[#0056BD] dark:text-white mt-2 break-normal mb-2 mt-20"
			>
				{@html question.question}
			</h1>
			{#if question.image !== null && game_mode !== 'kahoot'}
				<div class="flex justify-center lg:w-1/3 lg:w-full p-0 mt-5">
					<MediaComponent
						src={question.image}
						css_classes="max-h-[50vh] object-cover mx-auto mb-8 w-auto"
					/>
				</div>
			{/if}
		</div>
	{/if}
	{#if timer_res !== '0' && !showPlayerAnswers}
		{#if question.type === QuizQuestionType.ABCD || question.type === QuizQuestionType.VOTING}
		<div class="flex flex-col justify-start items-start w-full p-4 mt-0 ${game_mode !== 'normal' ? ' h-4/5' : ''}">
			<div class={`flex-grow relative w-full ${game_mode !== 'normal' ? 'h-full' : ''}`}>
				{#if game_mode !== 'normal'}
					<div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 rounded-full h-fit w-fit border-2 border-white shadow-2xl z-40">
						<CircularTimer bind:text={timer_res} bind:progress={circular_progress} color="#ef4444" />
					</div>
				{:else}
					<span
						class="fixed top-0 bg-red-500 h-8 transition-all"
						style="width: {(100 / parseInt(question.time)) * parseInt(timer_res)}vw"
					/>
				{/if}

				<div 
					class={`grid grid-rows-2 gap-2 w-full ${game_mode !== 'normal' ? 'h-full grid-flow-col auto-cols-auto' : 'grid-cols-2'}`}
					>
					{#each question.answers as answer, i}
						<button
							class="rounded-lg h-full  flex items-center justify-center disabled:opacity-60 border-4 border-white transition-all my-2"
							style="background-color: {answer.color ?? default_colors[i]}; color: {get_foreground_color(answer.color ?? default_colors[i])}"
							disabled={selected_answer !== undefined}
							on:click={() => selectAnswer(answer.answer)}
						>
							{#if game_mode === 'kahoot'}
								<img class="inline-block m-auto max-h-[30vh]" alt="Icon" src={kahoot_icons[i]} />
							{:else}
								<p class="m-auto button-text text-sm text-[{getTextColor(answer.color ?? '#fff')}] dark:text-[{getTextColor(answer.color ?? '#fff')}] sm:text-base md:text-lg lg:text-xl">{answer.answer}</p>
							{/if}
						</button>
					{/each}
				</div>
			</div>
		</div>
		{:else if question.type === QuizQuestionType.RANGE}
			<div class="fixed top-0 left-0 w-full bg-red-500 h-8 transition-all" style="width: {(100 / parseInt(question.time)) * parseInt(timer_res)}vw"></div>
			{#await import('svelte-range-slider-pips')}
				<Spinner />
			{:then c}
				<div class={`${game_mode !== 'normal' ? 'flex flex-col items-center justify-center w-full h-screen' : 'flex flex-col items-center justify-center w-full h-1/2'}`}>
					<div class="w-full h-1/5">
						<svelte:component
							this={c.default}
							bind:values={slider_value}
							bind:min={question.answers.min}
							bind:max={question.answers.max}
							id="pips-slider"
							pips
							float
							all="label"
							
							class="w-full !border-[#00EDFF] border-2 "
						/>
					</div>

					<div class="w-full max-w-xs flex justify-center mt-10">
						<button 
						type="button"
						class="bg-[#0056BD] border-[#fff] flex items-center border-2 gap-2 text-[#fff] font-semibold px-9 py-2 rounded-full disabled:cursor-not-allowed disabled:opacity-90"
						disabled={selected_answer !== undefined}
						on:click={() => selectRangeAnswer(slider_value[0])}
						>
							<RightArrow />
							{$t('words.submit')}
						</button>
						<!-- <BrownButton
							disabled={selected_answer !== undefined}
							on:click={() => selectRangeAnswer(slider_value[0])}
							class="w-full"
						>
							{$t('words.submit')}
						</BrownButton> -->
					</div>
				</div>
			{/await}
		{:else if question.type === QuizQuestionType.TEXT}
		<div class="flex flex-col items-center w-full {`${game_mode !== 'normal' ? 'justify-center h-screen' : ''}`}">
			<span
				class="fixed top-0 bg-red-500 h-8 transition-all"
				style="width: {(100 / parseInt(question.time)) * parseInt(timer_res)}vw"
			/>
			<div class="w-full max-w-md px-4 mt-10">
			  <label for="answer-input" class="block mb-2 mt-5 text-lg font-medium text-[#003FA7] dark:text-gray-200">Type your answer here:</label>
			  <input
				id="answer-input"
				type="text"
				bind:value={text_input}
				class="bg-white focus:ring placeholder-[#DCE1E7] text-black border-[#003FA7] border-2 shadow-inner bg-opacity-50 font-bold rounded-xl focus:ring-blue-500 block w-full py-4 px-3 dark:bg-[#0AEDFE]/20 dark:text-white dark:focus:ring-blue-500 outline-none transition text-center disabled:opacity-50 disabled:cursor-not-allowed "
				placeholder="Enter your answer"
			  />
			</div>
			<div class="mt-4 w-4/5 max-w-xs mx-auto flex justify-center">
				<button 
				type="button"
				class="bg-[#0056BD] border-[#fff] flex items-center border-2 gap-2 text-[#fff] font-semibold px-9 py-2 rounded-full disabled:cursor-not-allowed disabled:opacity-90"
				disabled={!text_input}
				on:click={() => {
					selectAnswer(text_input);
				}}
				>
					<RightArrow />
					{$t('words.submit')}
				</button>
				<!-- <BrownButton
					type="button"
					disabled={selected_answer}
					on:click={() => {
						selectAnswer(text_input);
					}}
				>
					{$t('words.submit')}
				</BrownButton> -->
			</div>
		</div>
		{:else if question.type === QuizQuestionType.RANGE}
			{#if solution === undefined}
				<Spinner />
			{:else}
				<p class="text-center">
					Every number between {solution.answers.min_correct} and {solution.answers
						.max_correct} was correct. You got {selected_answer}, so you have been
					{#if solution.answers.min_correct <= parseInt(selected_answer) && parseInt(selected_answer) <= solution.answers.max_correct}
						correct
					{:else}
						wrong.
					{/if}
				</p>
			{/if}
		{:else if question.type === QuizQuestionType.ORDER}
			<span
				class="fixed top-0 bg-red-500 h-8 transition-all"
				style="width: {(100 / parseInt(question.time)) * parseInt(timer_res)}vw"
			/>
			<div class="flex flex-col items-center justify-center w-full min-h-screen gap-4 px-4 mt-2">
				{#each question.answers as answer, i (answer.id)}
					<div
						class="w-full h-fit flex-row rounded-lg p-2 align-middle"
						animate:flip={{ duration: 100 }}
						style="color: {getTextColor(answer.color ?? '#004A93')}; background-color: {answer.color ?? '#004A93'};"
					>
						<button
							on:click={() => {
								question.answers = swapArrayElements(question.answers, i, i - 1);
							}}
							class="disabled:opacity-50 transition shadow-lg bg-black text-white bg-opacity-30 w-full flex justify-center rounded-lg p-2 hover:bg-opacity-20 transition"
							type="button"
							disabled={i === 0 || selected_answer}
						>
							<svg
								class="w-8 h-8"
								stroke-width="2"
								viewBox="0 0 24 24"
								fill="none"
								xmlns="http://www.w3.org/2000/svg"
								color="currentColor"
							>
								<path
									d="M12 22a2 2 0 110-4 2 2 0 010 4zM12 15V2m0 0l3 3m-3-3L9 5"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</button>
						<p class="w-full text-center p-2 text-2xl text-white">
							{answer.answer}
						</p>

						<button
							on:click={() => {
								question.answers = swapArrayElements(question.answers, i, i + 1);
							}}
							class="disabled:opacity-50 transition shadow-lg bg-black text-white bg-opacity-30 w-full flex justify-center rounded-lg p-2 hover:bg-opacity-20 transition"
							type="button"
							disabled={i === question.answers.length - 1 || selected_answer}
						>
							<svg
								class="w-8 h-8"
								stroke-width="2"
								viewBox="0 0 24 24"
								fill="none"
								xmlns="http://www.w3.org/2000/svg"
								color="currentColor"
							>
								<path
									d="M12 6a2 2 0 110-4 2 2 0 010 4zM12 9v13m0 0l3-3m-3 3l-3-3"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</button>
					</div>
				{/each}
				<div class="w-full flex justify-center mt-2">
					<button 
						type="button"
						class="bg-[#0056BD] border-[#fff] flex items-center border-2 gap-2 text-[#fff] font-semibold px-9 py-2 rounded-full disabled:cursor-not-allowed disabled:opacity-90"
						disabled={selected_answer}
						on:click={() => {
							select_complex_answer(question.answers);
						}}
						>
						
							<RightArrow />
							{$t('words.submit')}
					</button>
					<!-- <BrownButton
						type="button"
						disabled={selected_answer}
						on:click={() => {
							select_complex_answer(question.answers);
						}}>{$t('words.submit')}</BrownButton
						> -->
				</div>
			</div>
		{:else if question.type === QuizQuestionType.CHECK}
			{#if !showPlayerAnswers}
				{#await import('./questions/check.svelte')}
					<Spinner />
				{:then c}
					<svelte:component
						this={c.default}
						bind:question
						bind:selected_answer
						bind:text_answer
						bind:game_mode
						{timer_res}
						{circular_progress}
						on:submit={(event) => selectCheckAnswer(event.detail.selected_answer, event.detail.text_answer)}
					/>
				{/await}
			{/if}
		{/if}
		{:else if !showPlayerAnswers}
			<div class={`w-full flex justify-center items-center ${game_mode === 'normal' ? 'h-full' : 'min-h-screen'}`}>
				<h1 class="text-3xl dark:text-white text-[#0056BD] text-center p-3">
					{#if language}
						{en.admin_page.no_answers}
					{:else}
						{$t('admin_page.no_answers')}
					{/if}
				</h1>
			</div>
		{/if}
	<!-- Display the submitted answer -->
	{#if showPlayerAnswers}
	    <div class={`${game_mode !== 'normal' ? 'h-screen flex justify-center items-center' : ''}`}>
			<div class="px-4 text-center">
				<p class="text-lg font-semibold text-[#00529B] dark:text-[#fff] mt-10">Your answer:</p>
				{#if Array.isArray(selected_answer)}
				<ul class="list-disc list-inside mx-auto text-left text-[#00529B] inline-block dark:text-[#fff]">
					{#each selected_answer as ans}
					<li class="text-lg">{ans}</li>
					{/each}
				</ul>
				{:else}
				<p class="text-lg text-[#00529B] selected-ans bg-[#FFFFFF] font-bold p-4 rounded-lg mt-10">{selected_answer}</p>
				{/if}
			</div>
		</div>
	{/if}
</div>
<style>
	.selected-ans{
		box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25) inset; 
		border-radius: 16px
	}

</style>