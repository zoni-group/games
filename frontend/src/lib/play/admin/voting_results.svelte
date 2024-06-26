<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';

	export let data;
	export let question: Question;

	let quiz_answers = [];
	let quiz_colors = [];
	let answer_correct: boolean[] = [];

	for (const i of question.answers) {
		quiz_answers.push(i.answer);
		quiz_colors.push(i.color);
		answer_correct.push(i.right);
	}

	let sorted_data = {};
	for (const i of quiz_answers) {
		sorted_data[i] = 0;
	}

	// Function to clean and normalize text answers
	const cleanTextAnswer = (answer: string) => {
		return answer.trim().replace(/\s+/g, ' ');
	};

	// Count the answers
	for (const i of data) {
		let answer_found = false;
		for (const j of question.answers) {
			let submitted_answer = cleanTextAnswer(i.answer);
			let correct_answer = cleanTextAnswer(j.answer);
			if (!j.case_sensitive) {
				submitted_answer = submitted_answer.toLowerCase();
				correct_answer = correct_answer.toLowerCase();
			}
			if (submitted_answer === correct_answer) {
				sorted_data[j.answer] += 1;
				answer_found = true;
				break;
			}
		}
		if (!answer_found) {
			sorted_data[i.answer] += 1;
		}
	}
</script>

<div class="flex justify-center w-full">
	<div
		class="m-auto w-fit gap-4 flex flex-col"
		style="grid-template-columns: repeat({quiz_answers.length}, minmax(0, 1fr));"
	>
		<div class="flex gap-12">
			{#each quiz_answers as answer}
				<span class="text-center self-end mx-auto text-lg"
					>{#if sorted_data[answer] > 0}{sorted_data[answer]}{/if}</span
				>
			{/each}
		</div>
		<div class="flex gap-12">
			{#each quiz_answers as answer, i}
				<div
					class="w-20 self-end flex justify-center border border-black shadow-xl rounded"
					class:shadow-blue-500={answer_correct[i] &&
						question.type !== QuizQuestionType.VOTING}
					class:shadow-yellow-500={!answer_correct[i] &&
						question.type !== QuizQuestionType.VOTING}
					class:opacity-70={!answer_correct[i] &&
						question.type !== QuizQuestionType.VOTING}
					style="height: {(sorted_data[answer] * 20) /
						data.length}rem; background-color: {quiz_colors[i]
						? quiz_colors[i]
						: 'black'}"
				/>
			{/each}
		</div>
		<div class="flex gap-12">
			{#each quiz_answers as answer, i}
				<div class="w-20">
					<p
						class="-rotate-45 text-xl text-str"
						class:line-through={!answer_correct[i] &&
							question.type !== QuizQuestionType.VOTING && question.type !== QuizQuestionType.TEXT}
					>
						{@html answer}
					</p>
				</div>
			{/each}
		</div>
	</div>
</div>
