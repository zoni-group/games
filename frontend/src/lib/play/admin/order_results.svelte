<script lang="ts">
	import type { Question } from '$lib/quiz_types';

	export let data;
	export let question: Question;

	let quiz_answers = [];

	for (const i of question.answers) {
		quiz_answers.push(i.answer);
	}
</script>

<div class="flex justify-center w-full p-4">
	<div class="flex flex-col w-full max-w-2xl bg-white dark:bg-gray-800 shadow-lg rounded-lg p-4">
		<h2 class="text-xl font-bold text-center mb-4 dark:text-white">Correct Answers in Order</h2>
		<div class="flex flex-col gap-2">
			{#each quiz_answers as answer, i}
				<div class="flex items-center bg-gray-100 dark:bg-gray-700 rounded p-2">
					<div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 dark:bg-blue-700 text-white flex items-center justify-center font-bold mr-4">
						{i + 1}
					</div>
					<p class="flex-grow text-black dark:text-white">{@html answer}</p>
				</div>
			{/each}
		</div>
	</div>
</div>