<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	export let quiz: QuizData | undefined = undefined;

	const on_parent_click = (e: Event) => {
		if (e.target !== e.currentTarget) {
			return;
		}
		quiz = undefined;
	};
	const close_start_game_if_esc_is_pressed = (key: KeyboardEvent) => {
		if (key.code === 'Escape') {
			quiz = undefined;
		}
	};
	onMount(() => {
		document.body.addEventListener('keydown', close_start_game_if_esc_is_pressed);
	});
</script>

{#if quiz}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<div
		class="fixed w-full h-full top-0 flex bg-black bg-opacity-50 z-50 overflow-scroll"
		on:click={on_parent_click}
		transition:fade|local={{ duration: 100 }}
	>
		<div
			class="m-auto bg-white dark:bg-[#00529B] rounded shadow-2xl flex p-4 flex-col lg:w-2/3 w-11/12 h-5/6"
		>
			<h1 class="text-center text-5xl">{$t('words.analytics')}</h1>
			<section class="flex flex-col gap-2 mt-8">
				<h2 class="mx-auto text-2xl">{$t('words.rating')}</h2>
				<table class="w-fit mx-auto">
					<tr class="border-b-2 dark:border-gray-500 text-left border-gray-300">
						<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
							>{$t('words.like', { count: 2 })}</th
						>
						<th class="p-1 mx-auto">{$t('words.dislike', { count: 2 })}</th>
					</tr>
					<tr class="text-left">
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							>{quiz.likes}</td
						>
						<td class="mx-auto p-1">{quiz.dislikes}</td>
					</tr>
				</table>
			</section>
			<section class="flex flex-col gap-2 mt-8">
				<h2 class="mx-auto text-2xl">{$t('dashboard.views_n_plays')}</h2>
				<table class="w-fit mx-auto">
					<tr class="border-b-2 dark:border-gray-500 text-left border-gray-300">
						<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
							>{$t('words.view', { count: 2 })}</th
						>
						<th class="p-1 mx-auto">{$t('words.play', { count: 2 })}</th>
					</tr>
					<tr class="text-left">
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							>{quiz.views}</td
						>
						<td class="mx-auto p-1">{quiz.plays}</td>
					</tr>
				</table>
			</section>
			<section class="flex flex-col gap-2 mt-8">
				<h2 class="mx-auto text-2xl">{$t('words.info')}</h2>
				<p class="mx-auto max-w-[70%] text-center">
					{$t('dashboard.info_analytics')}
				</p>
			</section>
		</div>
	</div>
{/if}
