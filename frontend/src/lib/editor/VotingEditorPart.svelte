<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData } from '../quiz_types';
	import { fade } from 'svelte/transition';
	import { reach } from 'yup';
	import { getLocalization } from '$lib/i18n';
	import { VotingQuestionSchema } from '$lib/yupSchemas';
	import { get_foreground_color } from '$lib/helpers';
	import { toast } from '@zerodevx/svelte-toast';
	import Spinner from '$lib/Spinner.svelte';
	import MediaComponent from './MediaComponent.svelte';

	const { t } = getLocalization();

	const default_colors = ['#FFA800', '#00A3FF', '#FF1D38', '#00D749'];
	export let selected_question: number;
	export let data: EditorData;
	export let edit_id;
	let optionsType;
	let uppyOpen = false;

	if (!Array.isArray(data.questions[selected_question].answers)) {
		data.questions[selected_question].answers = [];
	}
	try {
		if (typeof data.questions[selected_question].answers[0].right === 'boolean') {
			data.questions[selected_question].answers = [];
		}
		// eslint-disable-next-line no-empty
	} catch {}

	const set_colors_if_unset = () => {
		for (let i = 0; i < data.questions[selected_question].answers.length; i++) {
			if (!data.questions[selected_question].answers[i].color) {
				data.questions[selected_question].answers[i].color = default_colors[i];
			}
		}
	};
	$: {
		set_colors_if_unset();
		data;
		selected_question;
	}
	const handleTextChange = (selectedQuestion: number, index: number) =>{
		if(data.questions[selectedQuestion].answers[index].answer.length >= 100){
			toast.push("Over 100 characters, please shorten the answer");	
		}else{
			console.log("Under 100");
		}
	}
	/*console.log(data.questions[selected_question].answers, 'moIn!', data.questions[selected_question].answers.length);
    onMount(() => {
        for (let i = 0; i < data.questions[selected_question].answers; i++) {
            console.log(data.questions[selected_question].answers[i], 'iterate');
            data.questions[selected_question].answers[i].right = undefined;
        }
    });*/
	$: optionsType = data.questions[selected_question].ansType;
</script>

<div class="grid grid-rows-2 grid-flow-col auto-cols-auto gap-4 w-full px-10">
	{#if Array.isArray(data.questions[selected_question].answers)}
		{#each data.questions[selected_question].answers as answer, index}
			<div
				out:fade|local={{ duration: 150 }}
				class="p-4 rounded-lg flex justify-center w-full transition relative"
				class:bg-yellow-500={!reach(VotingQuestionSchema, 'answer').isValidSync(
					answer.answer
				)}
				class:dark:bg-gray-500={answer.answer}
				class:bg-gray-300={answer.answer}
			>
				<button
					class="rounded-full absolute -top-2 -right-2 opacity-70 hover:opacity-100 transition"
					type="button"
					on:click={() => {
						data.questions[selected_question].answers.splice(index, 1);
						data.questions[selected_question].answers =
							data.questions[selected_question].answers;
					}}
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
				{#if optionsType === 'TEXT' || optionsType === undefined}
				<input
					bind:value={answer.answer}
					type="text"
					class="border-b-2 border-dotted w-5/6 text-center rounded-lg"
					style="background-color: {answer.color ??
						'transparent'}; color: {get_foreground_color(answer.color)}"
					maxlength="100"
					on:input={() => handleTextChange(selected_question,index)}
					placeholder={$t('editor.empty')}
				/>
				{:else}
					{#if answer.answer}
						<div class="flex justify-center pt-10 w-full h-72">
							<MediaComponent bind:src={answer.answer} />
							<div class="h-72 relative">
								<button
									class="rounded-full absolute -top-2 -right-2 opacity-70 hover:opacity-100 transition"
									type="button"
									on:click={() => {
										answer.answer = "";
									}}
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
							</div>
							
						</div>
					{:else}
						{#await import('$lib/editor/uploader.svelte')}
							<Spinner my_20={false} />
						{:then c}
							<svelte:component
								this={c.default}
								bind:modalOpen={uppyOpen}
								bind:edit_id
								selected_answer={index}
								bind:data
								bind:selected_question
								video_upload={true}
							/>
						{/await}
					{/if}
				{/if}
				<input
					class="rounded-lg p-1 border-black border"
					type="color"
					bind:value={answer.color}
					on:contextmenu|preventDefault={() => {
						answer.color = default_colors[index];
					}}
				/>
			</div>
		{/each}
	{/if}
	{#if data.questions[selected_question].answers.length === 0}
		<button
		class="p-4 rounded-lg bg-transparent border-gray-500 border-2 hover:bg-gray-300 transition dark:hover:bg-gray-600"
		type="button"
		in:fade|local={{ duration: 150 }}
		on:click={() => {
			data.questions[selected_question].answers = [
				...data.questions[selected_question].answers,
				{
					...{
						answer: '',
						image: undefined,
						color: default_colors[data.questions[selected_question].answers.length]
					}
				}
			];
			data.questions[selected_question].ansType = "TEXT";
		}}
		>
			<span class="italic text-center">Add Text Options</span>
		</button>
		<button
		class="p-4 rounded-lg bg-transparent border-gray-500 border-2 hover:bg-gray-300 transition dark:hover:bg-gray-600"
		type="button"
		in:fade|local={{ duration: 150 }}
		on:click={() => {
			data.questions[selected_question].answers = [
				...data.questions[selected_question].answers,
				{
					...{
						answer: '',
						image: undefined,
						color: default_colors[data.questions[selected_question].answers.length]
					}
				}
			];
			data.questions[selected_question].ansType = "IMAGE";
		}}
		>
			<span class="italic text-center">Add Image Options</span>
		</button>
	{/if}

	{#if data.questions[selected_question].answers.length < 4 && data.questions[selected_question].answers.length > 0}
		<button
			class="p-4 rounded-lg bg-transparent border-gray-500 border-2 hover:bg-gray-300 transition dark:hover:bg-gray-600"
			type="button"
			in:fade|local={{ duration: 150 }}
			on:click={() => {
				data.questions[selected_question].answers = [
					...data.questions[selected_question].answers,
					{
						...{
							answer: '',
							image: undefined,
							color: default_colors[data.questions[selected_question].answers.length]
						}
					}
				];
			}}
		>
			<span class="italic text-center">{$t('editor_page.add_an_answer')}</span>
		</button>
	{/if}
</div>
