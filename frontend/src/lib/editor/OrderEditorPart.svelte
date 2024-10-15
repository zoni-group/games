<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import type { EditorData, OrderQuizAnswer } from '$lib/quiz_types';
	import { fade } from 'svelte/transition';
	import { flip } from 'svelte/animate';
	import { get_foreground_color } from '$lib/helpers.ts';
	import { toast } from '@zerodevx/svelte-toast';
	import {dndzone} from 'svelte-dnd-action';

	const { t } = getLocalization();

	export let selected_question: number;
	export let data: EditorData;

	let parent_el: HTMLDivElement;
	const flipDurationMs = 200;
	let items;

	$: items = Array.isArray(data.questions[selected_question].answers) ? data.questions[selected_question].answers.map((answer, index) => ({
        id: [index], 
        answer: answer.answer, 
        color: answer.color
	})) : [];
	function handleSort(e) {
        items = e.detail.items;
		// sortData();
    }
	function handleFinalizeDND (e){
		items = e.detail.items;
		data.questions[selected_question].answers = items.map((item, i) => {
			return {
				answer: item.answer,
				color: item.color,
				id: [i]
			};
		});
	}
	const swapArrayElements = (arr: OrderQuizAnswer[], a: number, b: number): Array<any> => {
		let _arr = [...arr];
		let temp = _arr[a];
		_arr[a] = _arr[b];
		_arr[b] = temp;
		return _arr;
	};

	const move_item = (up: boolean, index: number) => {
		if (up) {
			data.questions[selected_question].answers = swapArrayElements(
				data.questions[selected_question].answers,
				index,
				index - 1
			);
		} else {
			data.questions[selected_question].answers = swapArrayElements(
				data.questions[selected_question].answers,
				index,
				index + 1
			);
		}
	};
	const sortData = () => {
		if (!Array.isArray(data.questions[selected_question].answers)) {
			data.questions[selected_question].answers = [];
		}
		for (let i = 0; i < data.questions[selected_question].answers.length; i++) {
			data.questions[selected_question].answers[i] = {
				answer: data.questions[selected_question].answers[i].answer,
				color: data.questions[selected_question].answers[i].color ?? undefined,
				id: [i]
			};
		}
	}
	sortData();
	const default_colors = ['#FFA800', '#00A3FF', '#FF1D38', '#00D749'];
	const set_colors_if_unset = () => {
		for (let i = 0; i < data.questions[selected_question].answers.length; i++) {
			if (!data.questions[selected_question].answers[i].color || default_colors.includes(data.questions[selected_question].answers[i].color)) {
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

<div class="w-full">
	<!-- <div class="flex flex-col w-full px-8" bind:this={parent_el}>
		{#each data.questions[selected_question].answers as answer, i (answer.id)}
			<div
				animate:flip={{ duration: 200 }}
				out:fade|local={{ duration: 150 }}
				class="p-4 rounded-lg flex justify-center w-full transition relative border border-gray-600 flex-row gap-4 m-2"
			>
				<button
					class="rounded-full absolute -top-2 -right-2 opacity-70 hover:opacity-100 transition"
					type="button"
					on:click={() => {
						data.questions[selected_question].answers.splice(i, 1);
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
				<div>
					<button
						on:click={() => {
							move_item(true, i);
						}}
						class="disabled:opacity-50 transition"
						type="button"
						disabled={i === 0}
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
					<button
						on:click={() => {
							move_item(false, i);
						}}
						class="disabled:opacity-50 transition"
						type="button"
						disabled={i === data.questions[selected_question].answers.length - 1}
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
				<input
					bind:value={answer.answer}
					type="text"
					class="border-b-2 border-dotted w-5/6 text-center rounded-lg bg-transparent outline-none"
					style="background-color: {answer.color}; color: {get_foreground_color(
						answer.color
					)}"
					maxlength="100"
					on:input={() => handleTextChange(selected_question,i)}
					placeholder={$t('editor.empty')}
				/>
				<input
					class="rounded-lg p-1 border-black border"
					type="color"
					bind:value={answer.color}
					on:contextmenu|preventDefault={() => {
						answer.color = null;
					}}
				/>
			</div>
		{/each}
	</div> -->
	<section 
			use:dndzone={{items, flipDurationMs}} 
			on:consider={handleSort} 
			on:finalize={handleFinalizeDND}
			class="flex flex-col items-center justify-start w-full gap-4 px-4 mt-10 py-4"
			style="overflow-y: auto; -webkit-overflow-scrolling: touch;"
		>
			{#each items as item, i (item.id)}
				<div 
					class="w-4/5 h-fit flex-row rounded-lg p-1 align-middle relative"
					animate:flip={{ duration: flipDurationMs }}
					style="color: {getTextColor(item.color ?? '#004A93')}; background-color: {item.color ?? '#004A93'};"
				>
				<button
					class="rounded-full absolute -top-2 -right-2 opacity-70 hover:opacity-100 transition"
					type="button"
					on:click={() => {
						data.questions[selected_question].answers.splice(i, 1);
						data.questions[selected_question].answers =
							data.questions[selected_question].answers;
							items = data.questions[selected_question].answers;
							set_colors_if_unset();
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
				<input
				bind:value={item.answer}
				type="text"
				name={`answer${i}`}
				class="border-b-2 border-dotted w-5/6 z-10 text-center rounded-lg bg-transparent outline-none"
				style="background-color: {item.color}; color: {get_foreground_color(
					item.color
				)}"
				maxlength="100"
				on:input={() => handleTextChange(selected_question,i)}
				placeholder={$t('editor.empty')}
			/>
			<input
				class="rounded-lg p-1 border-black border"
				type="color"
				name={`color${i}`}
				bind:value={item.color}
				on:contextmenu|preventDefault={() => {
					item.color = null;
				}}
			/>
				</div>
			{/each}
			
		</section>	

	<div class="px-8 flex w-full">
		{#if data.questions[selected_question].answers.length < 4}
			<button
				class="p-4 rounded-lg bg-transparent border-gray-500 border-2 hover:bg-gray-300 transition dark:hover:bg-gray-600 m-2 w-full"
				type="button"
				in:fade|local={{ duration: 150 }}
				on:click={() => {
					data.questions[selected_question].answers = [
						...data.questions[selected_question].answers,
						{
							...{
								answer: '',
								color: undefined,
								id: [data.questions[selected_question].answers.length]
							}
						}
					];
					set_colors_if_unset();
					items = data.questions[selected_question].answers;
					
				}}
			>
				<span class="italic text-center">{$t('editor_page.add_an_answer')}</span>
			</button>
		{/if}
	</div>
</div>
