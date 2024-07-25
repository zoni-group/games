<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';
	import Hoverable from '$lib/view_quiz/Hoverable.svelte';
	import { createTippy } from 'svelte-tippy';

	export let quiz: QuizData;

	let FeedBackButtonsHovered = {
		dislike: false,
		like: false
	};
	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'top'
	});

	const complete_action = async (positive: boolean) => {
		const res = await fetch(`/api/v1/community/rate/${quiz.id}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ type: positive ? 'LIKE' : 'DISLIKE' })
		});
		if (res.status === 409) {
			alert("You've already rated this activity!");
			return;
		} else if (!res.ok) {
			return;
		}
		if (positive) {
			quiz.likes += 1;
		} else {
			quiz.dislikes += 1;
		}
	};
</script>

<div class="flex flex-col border-[#004A93] dark:border-[#90CDF4] rounded border-2 p-2 gap-2">
	<div class="grid grid-cols-2 gap-2 group mx-auto">
		<Hoverable bind:hovering={FeedBackButtonsHovered.like}>
			<button
				class="rounded h-10 w-10 transition"
				use:tippy={{ content: 'Like this activity!' }}
				class:opacity-40={FeedBackButtonsHovered.dislike}
				on:click={() => complete_action(true)}
			>
				<!-- heroicons/thumb-up -->
				<svg xmlns="http://www.w3.org/2000/svg" height="32" width="32" viewBox="0 0 512 512"><!--!Font Awesome Pro 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2024 Fonticons, Inc.--><path class="fa-secondary" opacity=".4" fill="#198754" d="M351.1 89.4c5.2-26-11.7-51.3-37.7-56.5s-51.3 11.7-56.5 37.7L254.6 82c-6.6 33.2-24.8 63-51.2 84.2l-7.4 5.9c-22.8 18.2-36 45.8-36 75V272v48 38.3c0 32.1 16 62.1 42.7 79.9l38.5 25.7c15.8 10.5 34.3 16.1 53.3 16.1H392c26.5 0 48-21.5 48-48c0-3.6-.4-7-1.1-10.4c19.2-6.3 33.1-24.3 33.1-45.6c0-9.1-2.5-17.6-6.9-24.9c22.2-4.2 38.9-23.7 38.9-47.1c0-15.1-7-28.6-17.9-37.4c15.4-8 25.9-24.1 25.9-42.6c0-26.5-21.5-48-48-48H320c13.7-23.1 23.5-48.5 28.8-75.2l2.3-11.4z"/><path class="fa-primary" fill="#198754" d="M0 224c0-17.7 14.3-32 32-32H96c17.7 0 32 14.3 32 32V448c0 17.7-14.3 32-32 32H32c-17.7 0-32-14.3-32-32V224z"/></svg>
			</button>
		</Hoverable>
		<Hoverable bind:hovering={FeedBackButtonsHovered.dislike}>
			<button
				class="rounded h-10 w-10 transition"
				use:tippy={{ content: 'Dislike this activity!' }}
				class:opacity-40={FeedBackButtonsHovered.like}
				on:click={() => complete_action(false)}
			>
				<!-- heroicons/thumb-down -->
				<svg xmlns="http://www.w3.org/2000/svg" height="32" width="32" viewBox="0 0 512 512"><!--!Font Awesome Pro 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2024 Fonticons, Inc.--><path class="fa-secondary" opacity=".4" fill="#ef3e42" d="M351.1 422.6c5.2 26-11.7 51.3-37.7 56.5s-51.3-11.7-56.5-37.7L254.6 430c-6.6-33.2-24.8-63-51.2-84.2l-7.4-5.9c-22.8-18.2-36-45.8-36-75V240 192 153.7c0-32.1 16-62.1 42.7-79.9l38.5-25.7C257.1 37.6 275.6 32 294.5 32H392c26.5 0 48 21.5 48 48c0 3.6-.4 7-1.1 10.4C458.1 96.6 472 114.7 472 136c0 9.1-2.5 17.6-6.9 24.9c22.2 4.2 38.9 23.7 38.9 47.1c0 15.1-7 28.6-17.9 37.4c15.4 8 25.9 24.1 25.9 42.6c0 26.5-21.5 48-48 48H320c13.7 23.1 23.5 48.5 28.8 75.2l2.3 11.4z"/><path class="fa-primary" fill="#ef3e42" d="M0 352c0 17.7 14.3 32 32 32H96c17.7 0 32-14.3 32-32V128c0-17.7-14.3-32-32-32H32C14.3 96 0 110.3 0 128V352z"/></svg>
			</button>
		</Hoverable>
		<span class="text-center text-black dark:text-white" style="color: var(--main-color-green)">{quiz.likes}</span>
		<span class="text-center text-black dark:text-white" style="color: var(--main-color-danger)">{quiz.dislikes}</span>
	</div>
	<span class="w-full border-t-2 border-[#004A93] dark:border-[#90CDF4]" />
	<div class="mx-auto grid grid-cols-2 gap-2">
		<div class="flex flex-col">
			<!-- heroicons/legacy-outline/Play -->
			<svg xmlns="http://www.w3.org/2000/svg" height="32" width="40" viewBox="0 0 640 512"><!--!Font Awesome Pro 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2024 Fonticons, Inc.--><path class="fa-secondary" opacity=".4" fill="#004a93" d="M32 64C32 28.7 60.7 0 96 0H544c35.3 0 64 28.7 64 64V248.4c-17-15.2-39.4-24.4-64-24.4V64L96 64V224c-24.6 0-47 9.2-64 24.4V64z"/><path class="fa-primary" fill="#004a93" d="M96 384a64 64 0 1 0 0-128 64 64 0 1 0 0 128zM64 416c-35.3 0-64 28.7-64 64c0 17.7 14.3 32 32 32H160c17.7 0 32-14.3 32-32c0-35.3-28.7-64-64-64H64zm256-32a64 64 0 1 0 0-128 64 64 0 1 0 0 128zm-32 32c-35.3 0-64 28.7-64 64c0 17.7 14.3 32 32 32H384c17.7 0 32-14.3 32-32c0-35.3-28.7-64-64-64H288zm320-96a64 64 0 1 0 -128 0 64 64 0 1 0 128 0zM448 480c0 17.7 14.3 32 32 32H608c17.7 0 32-14.3 32-32c0-35.3-28.7-64-64-64H512c-35.3 0-64 28.7-64 64z"/></svg>
			<p class="mx-auto text-black dark:text-white" use:tippy={{ content: 'How often the activity was started' }}>
				{quiz.plays}
			</p>
		</div>
		<div class="flex flex-col">
			<!-- heroicons/legacy-outline/Eye -->
			<svg xmlns="http://www.w3.org/2000/svg" height="32" width="40" viewBox="0 0 640 512"><!--!Font Awesome Pro 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2024 Fonticons, Inc.--><path class="fa-secondary" opacity=".4" fill="#004a93" d="M160 64c0-35.3 28.7-64 64-64H576c35.3 0 64 28.7 64 64V352c0 35.3-28.7 64-64 64H336.8c-11.8-25.5-29.9-47.5-52.4-64H576V64L224 64v49.1C205.2 102.2 183.3 96 160 96V64zm252.7 75.3c-4.6-4.6-5.9-11.5-3.5-17.4s8.3-9.9 14.8-9.9h88c8.8 0 16 7.2 16 16v88c0 6.5-3.9 12.3-9.9 14.8s-12.9 1.1-17.4-3.5l-27-27L401 273c-9.4 9.4-24.6 9.4-33.9 0l-64-64c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l47 47 55.7-55.7-27-27z"/><path class="fa-primary" fill="#004a93" d="M160 320a96 96 0 1 0 0-192 96 96 0 1 0 0 192zm-26.7 32C59.7 352 0 411.7 0 485.3C0 500.1 11.9 512 26.7 512H293.3c14.7 0 26.7-11.9 26.7-26.7C320 411.7 260.3 352 186.7 352H133.3z"/></svg>
			<p class="mx-auto text-black dark:text-white" use:tippy={{ content: 'Activity views' }}>{quiz.views}</p>
		</div>
	</div>
</div>
