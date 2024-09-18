<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PrivateImageData } from '$lib/quiz_types';
	import Spinner from '$lib/Spinner.svelte';
	import type { EditorData } from '$lib/quiz_types';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { getLocalization } from '$lib/i18n';
	import { onMount } from 'svelte';
	enum AvailableUploadTypes {
		// eslint-disable-next-line no-unused-vars
		Image,
		// eslint-disable-next-line no-unused-vars
		Video,
		// eslint-disable-next-line no-unused-vars
		Library,
		// eslint-disable-next-line no-unused-vars
		Pixabay,
		// eslint-disable-next-line no-unused-vars
		Audio,
	}
	export let data: EditorData;
	export let selected_question: number;
	export let modalOpen: boolean;
	export let selected_type: AvailableUploadTypes | null;
	const { t } = getLocalization();

	const fetch_images = async (): Promise<PrivateImageData> => {
		const response = await fetch('/api/v1/storage/list/last?count=50');
		return await response.json();
	};
	let image_fetch = fetch_images();

	const set_image = (id: string) => {
		if (selected_question === undefined) {
			data.cover_image = id;
		} else if (selected_question === -1) {
			data.background_image = id;
		} else {
			data.questions[selected_question].image = id;
		}
		modalOpen = false;
	};
	
	let contentTypes: { [id: string]: string | null } = {};

	async function fetchContentType(url: string) {
		const response = await fetch(url, {
			method: 'HEAD'
		});
		return response.headers.get('Content-Type');
	}

	async function fetchContentTypes(images) {
		const promises = images.map(async (image) => {
			const contentType = await fetchContentType(`/api/v1/storage/download/${image.id}`);
			contentTypes = { ...contentTypes, [image.id]: contentType };
		});
		await Promise.all(promises);
	}

	onMount(async () => {
		const images = await image_fetch;
		fetchContentTypes(images);
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

{#await image_fetch}
	<Spinner />
{:then images}
	<div class="flex w-screen p-8 h-screen">
		<div
			class="flex flex-col w-1/3 m-auto overflow-scroll h-full rounded p-4 gap-4 bg-white dark:bg-gray-700" style="scrollbar-width: none;"
		>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<span class="material-symbols-outlined self-end bg-red-500 text-white rounded-xl p-2 cursor-pointer" on:click={() => {modalOpen = false; selected_type = null}} >
			Close
		</span>
			{#each images as image}
				<div class="rounded border-2 border-[#004A93] p-2 flex-col flex gap-2">
					<div class="w-full h-full flex items-center justify-center" >
						{#if contentTypes[image.id]?.startsWith('image')}
							<img
								src={`/api/v1/storage/download/${image.id}`}
								loading="lazy"
								alt={image.alt_text}
								class="object-contain w-1/2 h-full max-h-full rounded"
							/>
						{:else if contentTypes[image.id]?.startsWith('video')}
							<!-- svelte-ignore a11y-media-has-caption -->
							<video
								src={getVideoUrl(`/api/v1/storage/download/${image.id}`)}
								controls
								autoplay={false}
								loop={false}
								class="object-contain w-full h-full max-h-full rounded"
							>
								Your browser does not support the video tag.
							</video>
						{:else if contentTypes[image.id]?.startsWith('audio')}
							<div class="flex items-center justify-center h-full w-full">
								<!-- svelte-ignore a11y-media-has-caption -->
								<audio controls autoplay={false} loop={false} preload="auto" class="w-full">
									<source src={getAudioUrl(`/api/v1/storage/download/${image.id}`)} type="audio/mpeg" />
									Your browser does not support the audio element.
								</audio>
							</div>
						{:else}
							<p>Unsupported media type</p>
						{/if}
					</div>
					<p class="text-center">{image.filename ?? 'No name available'}</p>
					<BrownButton
						on:click={() => {
							set_image(image.id);
						}}>{$t('words.select')}</BrownButton
					>
				</div>
			{/each}
		</div>
	</div>
{/await}
