<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { Dashboard as SvelteDashboard } from '@uppy/svelte';
	import Uppy from '@uppy/core';
	import DropTarget from '@uppy/drop-target';
	import XHRUpload from '@uppy/xhr-upload';
	import ImageEditor from '@uppy/image-editor';
	import Dashboard from '@uppy/dashboard';
	import Compressor from '@uppy/compressor';
	import { fade } from 'svelte/transition';
	import BrownButton from '$lib/components/buttons/brown.svelte';

	// CSS imports
	import '@uppy/core/dist/style.css';
	import '@uppy/dashboard/dist/style.css';
	import '@uppy/drop-target/dist/style.css';
	// import '@uppy/file-input/dist/style.css'
	import '@uppy/image-editor/dist/style.css';
	import type { EditorData } from '../quiz_types';
	import { getLocalization } from '$lib/i18n';
	import { onMount } from 'svelte';
	import Library from '$lib/editor/uploader/Library.svelte';
	import Pixabay from '$lib/editor/uploader/Pixabay.svelte';

	const { t } = getLocalization();

	export let modalOpen = false;
	export let edit_id: string;
	export let data: EditorData;
	export let selected_question: number;
	export let video_upload = false;
	export let library_enabled = true;

	// eslint-disable-next-line no-undef
	let video_popup: undefined | WindowProxy = undefined;

	let selected_type: AvailableUploadTypes | null = null;

	// eslint-disable-next-line no-unused-vars
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

	const uppy = new Uppy()
		.use(DropTarget, {
			target: document.body
		})
		.use(Dashboard)
		.use(ImageEditor, {
			target: Dashboard,
			quality: 0.8
		})
		.use(Compressor, {
			quality: 0.6
		})
		.use(XHRUpload, {
			endpoint: `/api/v1/storage/`
		});
	const imageProps = {
		inline: true,
		restrictions: {
			maxFileSize: 10_490_000,
			maxNumberOfFiles: 1,
			allowedFileTypes: ['image/*']
			// allowedFileTypes: ['.gif', '.jpg', '.jpeg', '.png', '.svg', '.webp']
		}
	};
	const audioProps = {
		inline: true,
		restrictions: {
			maxFileSize: 10_490_000,
			maxNumberOfFiles: 1,
			allowedFileTypes: ['audio/mp3']
		}
	};

	let image_id;
	let audio_id;

	uppy.on('upload-success', (file, response) => {
		if (selected_type === AvailableUploadTypes.Image) {
			image_id = response.body.id;
		} else if (selected_type === AvailableUploadTypes.Audio) {
			audio_id = response.body.id;
		}
	});
	uppy.on('complete', (_) => {
		if (selected_question === undefined || selected_question === null) {
			if (selected_type === AvailableUploadTypes.Image || selected_type === AvailableUploadTypes.Audio) {
				data.cover_image = selected_type === AvailableUploadTypes.Image ? image_id : audio_id;
			}
		} else if (selected_question === -1) {
			if (selected_type === AvailableUploadTypes.Image) {
				data.background_image = image_id;
			} else if (selected_type === AvailableUploadTypes.Audio) {
				data.background_audio = audio_id;
			}
		} else {
			if (selected_type === AvailableUploadTypes.Image) {
                if (!data.questions[selected_question]) {
                    data.questions[selected_question] = {};
                }
				data.questions[selected_question].image = image_id;
			} else if (selected_type === AvailableUploadTypes.Audio) {
                if (!data.questions[selected_question]) {
                    data.questions[selected_question] = {};
                }
				data.questions[selected_question].image = audio_id;
			}
		}

		modalOpen = false;
		selected_type = null;
	});

	onMount(() => {
		window.addEventListener('storage', (e) => {
			if (e.key !== 'video_upload_id') {
				return;
			}
			localStorage.removeItem('video_upload_id');
			if (selected_question === undefined || selected_question === null) {
				data.cover_image = e.newValue;
			} else {
				data.questions[selected_question].image = e.newValue;
			}
			selected_type = null;
		});
	});

	const upload_video = async () => {
		video_popup = window.open(
			'/edit/videos',
			'_blank',
			'popup=true,toolbar=false,menubar=false,location=false,'
		);
		video_popup.addEventListener('beforeunload', () => {
			video_popup = undefined;
		});
	};

	const handle_on_click = (e: Event) => {
		if (e.target === e.currentTarget) {
			modalOpen = false;
			selected_type = null;
		}
	};
	onMount(() => {
		window.addEventListener('keydown', (e: KeyboardEvent) => {
			if (e.key === 'Escape') {
				modalOpen = false;
				selected_type = null;
			}
		});
	});
</script>

{#if modalOpen}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<div
		class="w-screen h-screen fixed top-0 left-0 bg-opacity-50 bg-black z-20 flex justify-center"
		on:click={handle_on_click}
		transition:fade|local={{ duration: 100 }}
	>
		{#if selected_type === null}
			<div class="m-auto h-auto bg-white dark:bg-gray-700 p-4 rounded">
				<h1 class="text-3xl text-center mb-4">{$t('uploader.select_upload_type')}</h1>
				<div class="flex flex-row gap-4">
					<div class="w-full">
						<BrownButton
							on:click={() => {
								selected_type = AvailableUploadTypes.Image;
							}}
							>{$t('words.image')}
						</BrownButton>
					</div>
					<div class="w-full">
						<BrownButton
							disabled={!video_upload}
							on:click={() => {
								selected_type = AvailableUploadTypes.Video;
							}}
							>{$t('words.video')}
						</BrownButton>
					</div>
					{#if library_enabled}
						<div class="w-full">
							<BrownButton
								on:click={() => {
									selected_type = AvailableUploadTypes.Library;
								}}
								>{$t('words.library')}
							</BrownButton>
						</div>
					{/if}
					<div class="w-full">
						<BrownButton
							on:click={() => {
								selected_type = AvailableUploadTypes.Pixabay;
							}}
							>Pixabay
						</BrownButton>
					</div>
					<div class="w-full">
						<BrownButton
							disabled={!video_upload}
							on:click={() => {
								selected_type = AvailableUploadTypes.Audio;
							}}
							>{$t('words.audio')}
						</BrownButton>
					</div>
				</div>
			</div>
		{:else if selected_type === AvailableUploadTypes.Image}
			<div class="m-auto w-1/3 h-5/6" transition:fade|local={{ duration: 100 }}>
				<div>
					<SvelteDashboard {uppy} width="100%" {imageProps} />
				</div>
			</div>
		{:else if selected_type === AvailableUploadTypes.Video}
			<div
				class="m-auto w-1/3 h-auto bg-white dark:bg-gray-700 p-4 rounded"
				transition:fade|local={{ duration: 100 }}
			>
				<h1 class="text-3xl text-center mb-4">{$t('uploader.upload_a_video')}</h1>
				{#if video_popup}
					<p class="text-center">
						{$t('uploader.upload_video_popup_notice')}
					</p>
				{:else}
					<BrownButton on:click={upload_video} type="button"
						>{$t('uploader.upload_video')}</BrownButton
					>
				{/if}
			</div>
		{:else if selected_type === AvailableUploadTypes.Library}
			<div>
				<Library bind:data {selected_question} bind:modalOpen />
			</div>
		{:else if selected_type === AvailableUploadTypes.Pixabay}
			<div>
				<Pixabay bind:data {selected_question} bind:modalOpen />
			</div>
		{:else if selected_type === AvailableUploadTypes.Audio}
			<div class="m-auto w-1/3 h-5/6" transition:fade|local={{ duration: 100 }}>
				<div>
					<SvelteDashboard {uppy} width="100%" {audioProps} />
				</div>
			</div>
		{/if}
	</div>
{/if}
<div class="flex justify-center w-full pt-10" transition:fade|local>
	<button
		class="rounded-lg p-4 flex justify-center bg-transparent border-gray-500 border-2 w-1/2 hover:bg-gray-300 dark:hover:bg-gray-600 transition"
		type="button"
		on:click={() => {
			modalOpen = true;
		}}
		><span class="italic">{$t('uploader.add_image')}</span>
		<svg
			class="w-6 h-6 inline-block"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
			xmlns="http://www.w3.org/2000/svg"
		>
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
			/>
		</svg>
	</button>
</div>
