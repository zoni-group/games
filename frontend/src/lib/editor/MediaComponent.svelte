<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { browser } from '$app/environment';
	import { fade } from 'svelte/transition';
	import { thumbHashToDataURL } from 'thumbhash';

	export let src: string;
	export let css_classes = 'max-h-64 h-auto w-auto';
	export let added_thumbhash_classes = 'h-full';
	export let muted = false;
	export let allow_fullscreen = true;
	let type: 'img' | 'video' | 'audio' | undefined = undefined;

	let img_data;
	let thumbhash_data: string;

	function base64ToBytes(base64: string): Uint8Array {
		const binString = atob(base64);
		return Uint8Array.from(binString, (m) => m.codePointAt(0));
	}

	const get_media = async () => {
		if (!browser) {
			return;
		}
		const res = await fetch(`/api/v1/storage/info/${src}`);
		const fileType = res.headers.get('Content-Type');
		if (fileType.includes('video')) {
			type = 'video';
		} else if (fileType.includes('audio')) {
			type = 'audio';
		} else {
			type = 'img';
			thumbhash_data = thumbHashToDataURL(base64ToBytes(res.headers.get('x-thumbhash')));
			const data = await fetch(`/api/v1/storage/download/${src}`);
			img_data = {
				data: URL.createObjectURL(await data.blob()),
				alt_text: new TextDecoder().decode(base64ToBytes(res.headers.get('X-Alt-Text')))
			};
			thumbhash_data = undefined;
		}
	};
	const update_url = () => {
		media = get_media();
	};
	let media = get_media();
	$: {
		src;
		update_url();
	}

	let fullscreen_open = false;

	const open_fullscreen = () => {
		if (!allow_fullscreen) {
			return;
		}
		fullscreen_open = true;
	};
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

{#await media}
	<!-- svelte-ignore a11y-missing-attribute -->
	<img src={thumbhash_data} class={`${css_classes} ${added_thumbhash_classes}`} />
{:then data}
	{#if type === 'img'}
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<img
			in:fade={{ duration: 300 }}
			src={img_data.data}
			alt={img_data.alt_text ?? 'Not available'}
			class={css_classes}
			on:click={() => open_fullscreen()}
		/>
	{:else if type === 'video'}
		<video
			class={css_classes}
			disablepictureinpicture
			controls
			autoplay={false}
			loop={false}
			{muted}
			preload="metadata"
		>
			<source src={getVideoUrl(`/api/v1/storage/download/${src}`)} />			
		</video>
	{:else if type === 'audio'}
		<video
			class={css_classes}
			disablepictureinpicture
			controls
			autoplay={false}
			loop={false}
			{muted}
			preload="metadata"
		>
			<source src={getAudioUrl(`/api/v1/storage/download/${src}`)} />			
		</video>
	{:else}
		<p>Unknown media type</p>
	{/if}
{/await}

{#if fullscreen_open}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<div
		class="fixed top-0 left-0 z-50 w-screen h-screen bg-black bg-opacity-50 fle p-2"
		transition:fade={{ duration: 80 }}
		on:click={() => (fullscreen_open = false)}
	>
		<img
			src={img_data.data}
			alt={img_data.alt_text ?? 'Not available'}
			class="object-cover rounded m-auto max-h-full max-w-full"
		/>
	</div>
{/if}
