<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onMount } from 'svelte';

	export let title: string;
	export let description: string;
	export let cover_image: string | undefined;
	let contentType: string | null = null;

	async function fetchContentType(url: string) {
		const response = await fetch(url, {
			method: 'HEAD'
		});
		return response.headers.get('Content-Type');
	}

	onMount(async () => {
		if (cover_image) {
			contentType = await fetchContentType(`/api/v1/storage/download/${cover_image}`);
		}
	});

	// Function to ensure the .mp4 extension is present
	function getVideoUrl(url) {
    	if (!url.endsWith('.mp4')) {
      		return `${url}.mp4`;
    	}
    	return url;
  	}

	// Function to ensure the .mp3 extension is present
	function getAudioUrl(url) {
    	if (!url.endsWith('.mp3')) {
      		return `${url}.mp3`;
    	}
    	return url;
  	}
</script>

<div class="flex flex-col justify-center w-screen h-screen p-4">
	<h1 class="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl text-center break-words">
		{@html title}
	</h1>
	<p class="text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl pt-4 sm:pt-6 md:pt-8 text-center break-words  dark:text-white">
		{@html description}
	</p>
	{#if cover_image}
		<div class="flex justify-center align-middle items-center">
			<div class="h-[20vh] sm:h-[25vh] md:h-[30vh] lg:h-[35vh] xl:h-[40vh] m-auto w-auto mt-8 sm:mt-10 md:mt-12">
				{#if contentType?.startsWith('image')}
					<img
						class="max-h-full max-w-full block"
						src={`/api/v1/storage/download/${cover_image}`}
						alt="Not provided"
					/>
				{:else if contentType?.startsWith('video')}
					<!-- svelte-ignore a11y-media-has-caption -->
					<video
						class="max-h-full max-w-full block"
						src={getVideoUrl(`/api/v1/storage/download/${cover_image}`)}
						controls
						autoplay={false}
						loop={false}
					>
						Your browser does not support the video tag.
					</video>
				{:else if contentType?.startsWith('audio')}
					<!-- svelte-ignore a11y-media-has-caption -->
					<video
						class="max-h-full max-w-full block"
						src={getAudioUrl(`/api/v1/storage/download/${cover_image}`)}
						controls
						autoplay={false}
						loop={false}
					>
						Your browser does not support the video tag.
					</video>
				{:else}
					<p>Unsupported media type</p>
				{/if}
			</div>
		</div>
	{/if}
</div>
