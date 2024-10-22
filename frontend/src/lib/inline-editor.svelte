<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import BalloonEditor from '@ckeditor/ckeditor5-build-balloon';
	import { validateSchema } from '@felte/validator-yup';
	// import Essentials from '@ckeditor/ckeditor5-essentials/src/essentials';
	// import Bold from '@ckeditor/ckeditor5-basic-styles/src/bold.js';
	// import Italic from '@ckeditor/ckeditor5-basic-styles/src/italic.js';
	// import Strikethrough from '@ckeditor/ckeditor5-basic-styles/src/strikethrough';
	// import Subscript from '@ckeditor/ckeditor5-basic-styles/src/subscript.js';
	// import Superscript from '@ckeditor/ckeditor5-basic-styles/src/superscript.js';
	// import Autoformat from "@ckeditor/ckeditor5-autoformat/src/autoformat"

	export let text = '';
	export let data;
	const triggerChange = () => {
		text = editor.getData();
		validateSchema(data); //used to trigger validation every time data changes
	};

	import { onMount } from 'svelte';

	let html_el;

	$: text = text.replace('<p>', '').replace('</p>', '').replaceAll('&nbsp;','');

	/*	Editor.builtinPlugins = [
		Autoformat,
		Bold,
		Essentials,
		Italic,
		Paragraph,
		Strikethrough,
		Subscript,
		Superscript,
		TextTransformation
	];*/
	/*Editor.defaultConfig = {
	toolbar: {
		items: [
			'bold',
			'italic',
			'strikethrough',
			'superscript',
			'subscript',
			'|',
			'undo',
			'redo'
		]
	},
	language: 'en'
};*/
	let editor;
	onMount(() => {
		// BalloonEditor.builtinPlugins = [Strikethrough]
		BalloonEditor.create(html_el, {
			// plugins: [Strikethrough],
			config: {
				enterMode: BalloonEditor.ENTER_DIV,
				shiftEnterMode: BalloonEditor.ENTER_BR
			},
			toolbar: [
				'bold',
				'italic',
				'strikethrough',
				'superscript',
				'subscript',
				'|',
				'undo',
				'redo'
			]
		})
			.then((newEditor) => {
				editor = newEditor;
				editor.setData(text);
				editor.model.document.on('change:data', () => {
					triggerChange();
				});
			})
			.catch((error) => {
				console.error('There was a problem initializing the editor.', error);
			});
	});
</script>

<div class="md:w-fit w-full md:m-auto mx-4 rounded-lg border-slate-500 border">
	<div
		bind:this={html_el}
		contenteditable="true"
		class="rounded-lg border-slate-500 border bg-slate-300 text-center md:w-fit w-full h-fit dark:text-white text-black resize-none dark:bg-slate-500 min-w-[5rem]"
	/>
</div>
