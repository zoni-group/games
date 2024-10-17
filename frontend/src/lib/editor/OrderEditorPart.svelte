<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import type { EditorData } from '$lib/quiz_types';
	import { get_foreground_color } from '$lib/helpers.ts';
	import { toast } from '@zerodevx/svelte-toast';
	import { dndzone, SHADOW_ITEM_MARKER_PROPERTY_NAME } from 'svelte-dnd-action';
	import { fade } from 'svelte/transition';
	import { cubicIn } from 'svelte/easing';

	const { t } = getLocalization();

	export let selected_question: number;
	export let data: EditorData;
	let oldSelectedQuestion = -1;
	const default_colors = ['#FFA800', '#00A3FF', '#FF1D38', '#00D749'];

	let idCounter = 0;
	let items = [];

    // Keep track of the previous selected question
    let prevSelectedQuestion = selected_question;

	// Initialize items for drag-and-drop
	// Reactive statement to update items when selected_question changes
	// Update items only when selected_question changes
	$: if (selected_question !== prevSelectedQuestion) {
        items = data.questions[selected_question].answers.map((answer, index) => {
            if (typeof answer.id !== 'number') {
                answer.id = idCounter++;
            }
            return {
                ...answer,
                color: answer.color || default_colors[index % default_colors.length],
            };
        });
        prevSelectedQuestion = selected_question;
    }

	const handleTextChange = (selectedQuestion: number, index: number) => {
		data.questions[selectedQuestion].answers = [...data.questions[selectedQuestion].answers]; // Trigger reactivity
		if (data.questions[selectedQuestion].answers[index].answer.length >= 100) {
			toast.push("Over 100 characters, please shorten the answer");
		}
	};

	// Sort handler when items are rearranged using drag-and-drop
	function handleSort(e) {
		items = e.detail.items;
		data.questions[selected_question].answers = items;
		data.questions[selected_question].answers = [...data.questions[selected_question].answers]; // Ensure reactivity
	}

	// Add new answer functionality
	function addAnswer() {
		const newItem = {
			answer: '',
			color: default_colors[items.length % default_colors.length], // Use default colors in sequence
			id: idCounter++, // Assign a unique id
		};
		items = [...items, newItem]; // Ensure reactivity
		data.questions[selected_question].answers = items;
		data.questions[selected_question].answers = [...data.questions[selected_question].answers]; // Trigger reactivity
	}

	// Remove answer functionality
	function removeAnswer(index: number) {
		data.questions[selected_question].answers.splice(index, 1);
		items = [...data.questions[selected_question].answers];
		data.questions[selected_question].answers = [...data.questions[selected_question].answers]; // Trigger reactivity
	}
	

	$: {
		if(oldSelectedQuestion !== selected_question){
			oldSelectedQuestion = selected_question;
			items = data.questions[selected_question].answers.map((answer, index) => {
				if (typeof answer.id !== 'number') {
					answer.id = idCounter++;
				}
				return {
					...answer,
					color: answer.color || default_colors[index % default_colors.length], // Apply default color if undefined
				};
			});
		}
	}
</script>

<style>
	.dnd-item {
		transition: background-color 0.2s, transform 0.2s;
	}

	.dnd-item.dragging {
		transform: scale(1.05);
	}

	.dnd-item.empty {
		border: 2px dashed #ccc;
	}

	.answer-input.empty::placeholder {
		color: #888;
	}
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

<div class="w-full">
	<!-- Drag-and-drop zone -->
	<div
		class="flex flex-col w-full px-8"
		use:dndzone={{ items, flipDurationMs: 200, dropTargetStyle:{"outline": "none"} ,dropTargetClasses: ["border-0","bg-slate-300/50","shadow-lg", "outline-none","rounded-lg","shadow-black","transition","ease-in-out"] }}
		on:consider={handleSort}
		on:finalize={handleSort}
	>
		{#each items as answer, i (answer.id)}
			<div
				class="p-4 rounded-lg flex justify-center w-full transition relative border border-gray-600 flex-row gap-4 m-2 dnd-item {answer.answer === '' ? 'empty' : ''}"
				style="background-color: {answer.color}; color: {get_foreground_color(answer.color)}"
			>
				<!-- Delete button -->
				<button
					class="rounded-full absolute -top-2 -right-2 opacity-70 hover:opacity-100 transition"
					type="button"
					on:mousedown|stopPropagation
					on:touchstart|stopPropagation
					on:click={() => removeAnswer(i)}
				>
					<svg
						class="w-6 h-6 bg-red-500 rounded-full"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
				</button>

				<!-- Answer input field -->
				<input
					bind:value={answer.answer}
					type="text"
					class="border-b-2 border-dotted w-5/6 text-center rounded-lg bg-transparent outline-none answer-input {answer.answer === '' ? 'empty' : ''}"
					maxlength="100"
					on:input={() => handleTextChange(selected_question, i)}
					placeholder={$t('editor.empty')}
				/>

				<!-- Color picker -->
				<input
					class="rounded-lg p-1 border-black border"
					type="color"
					bind:value={answer.color}
					title="Pick a color"
					on:contextmenu|preventDefault={() => { answer.color = default_colors[i % default_colors.length]; }}
				/>
				{#if answer[SHADOW_ITEM_MARKER_PROPERTY_NAME]}
							<div in:fade={{duration:200, easing: cubicIn}} class='custom-shadow-item w-full h-full flex-row rounded-lg p-1 align-middle opacity-10' style="color: white; ">
								<p class="w-full text-center p-1 text-lg text-white">
									<input
										bind:value={answer.answer}
										type="text"
										class="border-b-2 border-dotted w-5/6 text-center rounded-lg bg-transparent outline-none answer-input {answer.answer === '' ? 'empty' : ''}"
										maxlength="100"
										on:input={() => handleTextChange(selected_question, i)}
										placeholder={$t('editor.empty')}
									/>
								</p>
							</div>
						{/if}
			</div>
		{/each}
	</div>

	<!-- Add new answer button -->
	<div class="px-8 flex w-full">
		{#if items.length < 4}
			<button
				class="p-4 rounded-lg bg-transparent border-gray-500 border-2 hover:bg-gray-300 transition dark:hover:bg-gray-600 m-2 w-full"
				type="button"
				on:click={addAnswer}
			>
				<span class="italic text-center">{$t('editor_page.add_an_answer')}</span>
			</button>
		{/if}
	</div>
</div>
