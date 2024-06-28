<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { onMount } from 'svelte';

	export let data: PageData;
	let contentTypes: { [id: string]: string | null } = {};

	async function fetchContentType(url: string) {
		const response = await fetch(url, {
			method: 'HEAD'
		});
		return response.headers.get('Content-Type');
	}

	async function fetchContentTypes() {
		const promises = data.quizzes.map(async (quiz) => {
			if (quiz.cover_image) {
				const contentType = await fetchContentType(`/api/v1/storage/download/${quiz.cover_image}`);
				contentTypes = { ...contentTypes, [quiz.cover_image]: contentType };
			}
		});
		await Promise.all(promises);
	}

	onMount(() => {
		fetchContentTypes();
	});
</script>

<div class="flex flex-col p-2">
	{#each data.quizzes as quiz}
		<div class="border-2 border-[#004A93] rounded w-full h-[20vh] p-2 flex flex-col gap-2">
			<div class="grid grid-cols-3 h-full">
				<div class="hidden lg:flex w-auto h-full items-center relative">
					{#if quiz.cover_image}
						{#if contentTypes[quiz.cover_image]?.startsWith('image')}
							<img
								src={`/api/v1/storage/download/${quiz.cover_image}`}
								alt="user provided"
								loading="lazy"
								class="shrink-0 max-w-full max-h-full absolute rounded"
							/>
						{:else if contentTypes[quiz.cover_image]?.startsWith('video')}
							<!-- svelte-ignore a11y-media-has-caption -->
							<video
								src={`/api/v1/storage/download/${quiz.cover_image}`}
								class="shrink-0 max-w-full max-h-full absolute rounded"
								controls
							>
								Your browser does not support the video tag.
							</video>
						{:else}
							<p>Unsupported media type</p>
						{/if}
					{/if}
				</div>
				<div class="my-auto mx-auto max-h-full overflow-hidden">
					<p class="text-xl text-center">{@html quiz.title}</p>
					<p class="text-sm text-center text-clip overflow-hidden">
						{@html quiz.description ?? ''}
					</p>
				</div>
				<div class="flex justify-center">
					<p class="m-auto">Questions: {quiz.questions.length}</p>
				</div>
			</div>
			<div class="flex w-full">
				<BrownButton href="/view/{quiz.id}?mod=true&autoExpand=true&autoReturn=true"
					>View</BrownButton
				>
			</div>
		</div>
	{/each}
</div>
<div class="flex">
	<div class="grid grid-cols-3 mx-auto">
		<BrownButton disabled={data.page === '1'} href="/moderation?page={parseInt(data.page) + 1}"
			>Previous Page</BrownButton
		>
		<p class="m-auto">Page {data.page}</p>
		<BrownButton
			disabled={data.quizzes.length !== 20}
			href="/moderation?page={parseInt(data.page) - 1}">Next Page</BrownButton
		>
	</div>
</div>
