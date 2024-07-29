<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Question } from '$lib/quiz_types';
	import { get_foreground_color } from '$lib/helpers';
	import { kahoot_icons } from '$lib/play/kahoot_mode_assets/kahoot_icons';
	import CircularTimer from '$lib/play/circular_progress.svelte';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import RightArrow from '$lib/icons/rightArrow.svelte';

	const default_colors = ['#C8E6C9', '#FFE0B2', '#FFF9C4', '#B3E5FC'];
	export let question: Question;
	export let selected_answer = '';
	export let text_answer = [];
	export let game_mode;

	export let timer_res;
	export let circular_progress;

	let _selected_answers = [false, false, false, false];
	let _text_answers = new Array(question.answers.length).fill(false);

	const dispatch = createEventDispatcher();

	const selectAnswer = (i: number) => {
		_selected_answers[i] = !_selected_answers[i];
		selected_answer = '';
		for (let i = 0; i < _selected_answers.length; i++) {
			if (_selected_answers[i]) {
				selected_answer += String(i);
			}
		}
		selected_answer = selected_answer;
		console.log(_selected_answers, selected_answer);

		_text_answers[i] = !_text_answers[i];
    	const text_answers = question.answers.filter((_, index) => _text_answers[index]).map(a => a.answer);
    	text_answer = text_answers;
    	console.log(_text_answers, text_answer);
	};

	const handleSubmit = () => {
		selectAnswer(selected_answer);
    	dispatch('submit', { selected_answer, text_answer });
	};
	
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

<div class="flex flex-col justify-start items-start w-full p-4 mt-0 ${game_mode !== 'normal' ? ' h-4/5' : ''}">
	<div class={`flex-grow relative w-full ${game_mode !== 'normal' ? 'h-full' : ''}`}>
		{#if game_mode !== 'normal'}
			<div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 rounded-full h-fit w-fit border-2 border-black shadow-2xl z-40">
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
					class="rounded-lg h-full w-9/10 flex items-center justify-center disabled:opacity-60 border-2 border-black transition-all my-2"
					style="background-color: {answer.color ?? default_colors[i]}; color: {get_foreground_color(answer.color ?? default_colors[i])}"
					on:click={() => selectAnswer(i)}
					class:opacity-100={_selected_answers[i]}
					class:opacity-50={!_selected_answers[i]}
				>
					{#if game_mode === 'kahoot'}
						<img class="inline-block m-auto max-h-[30vh]" alt="Icon" src={kahoot_icons[i]} />
					{:else}
						<p class="m-auto button-text text-sm sm:text-base md:text-lg lg:text-xl" style="color: {getTextColor(answer.color ?? '#004A93')}">{answer.answer}</p>
					{/if}
				</button>
			{/each}
		</div>
	</div>
	<div class="w-full mx-auto text-center py-4">
				<button 
					type="button"
					class="bg-gradient-to-r from-[#FE700A] via-[#FFFFFF] to-[#FF4D00] shadow-x rounded-full p-1 "
					disabled={!selected_answer}
					on:click={handleSubmit}
					>
					<span class="bg-[#FFE500] p-2 px-6 flex w-full rounded-full uppercase text-[#00529B] font-semibold items-center justify-center gap-3" >
						<RightArrow />
						Submit
					</span>
				</button>
		<!-- <BrownButton
			disabled={!selected_answer}
			on:click={handleSubmit}
		>
			Submit
		</BrownButton> -->
	</div>
</div>
