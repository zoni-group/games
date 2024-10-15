<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import type { EditorData, OrderQuizAnswer } from '$lib/quiz_types';
	import { get_foreground_color } from '$lib/helpers.ts';
	import { toast } from '@zerodevx/svelte-toast';
	import { dndzone } from 'svelte-dnd-action';
  
	const { t } = getLocalization();
  
	export let selected_question: number;
	export let data: EditorData;
  
	// Initialize items for drag-and-drop
	let items = data.questions[selected_question].answers.map((answer, i) => ({
	  ...answer,
	  id: i,
	  color: answer.color || '#0000FF', // Default color if undefined
	}));

	const handleTextChange = (selectedQuestion: number, index: number) => {
	  if (data.questions[selectedQuestion].answers[index].answer.length >= 100) {
		toast.push("Over 100 characters, please shorten the answer");
	  }
	};
  
	// Sort handler when items are rearranged using drag-and-drop
	function handleSort(e) {
	  items = e.detail.items;
	  data.questions[selected_question].answers = items;
	}
  
	// Add new answer functionality
	function addAnswer() {
	  const newItem = {
		answer: '',
		color: '#0000FF', // Default color for new items
		id: items.length,
	  };
	  items = [...items, newItem]; // Ensure reactivity
	  data.questions[selected_question].answers = items;
	}

	// Remove answer functionality
	function removeAnswer(index: number) {
	  data.questions[selected_question].answers.splice(index, 1);
	  items = [...data.questions[selected_question].answers];
	}
</script>

<div class="w-full">
	<!-- Drag-and-drop zone -->
	<div
		class="flex flex-col w-full px-8"
		use:dndzone={{ items, flipDurationMs: 200 }}
		on:consider={handleSort}
		on:finalize={handleSort}
	>
		{#each items as answer, i (answer.id)}
			<div
				class="p-4 rounded-lg flex justify-center w-full transition relative border border-gray-600 flex-row gap-4 m-2"
				style="background-color: {answer.color}; color: {get_foreground_color(answer.color)}"
			>
				<!-- Delete button -->
				<button
					class="rounded-full absolute -top-2 -right-2 opacity-70 hover:opacity-100 transition"
					type="button"
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
					class="border-b-2 border-dotted w-5/6 text-center rounded-lg bg-transparent outline-none"
					maxlength="100"
					on:input={() => handleTextChange(selected_question, i)}
					placeholder={$t('editor.empty')}
				/>

				<!-- Color picker -->
				<input
					class="rounded-lg p-1 border-black border"
					type="color"
					bind:value={answer.color}
					on:contextmenu|preventDefault={() => { answer.color = '#ffffff'; }}
				/>
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
