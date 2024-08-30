<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import btn_img from "$lib/assets/all/start_btn.webp";
	export let disabled = false;
	export let flex = false;

	export let href: undefined | string = undefined;
	export let target: undefined | string = '_self';
	export let theme: "light" | "dark" | "primary" | "secondary" | "info" | "success" | "warning" | "danger" = "primary";
</script>

<style>
	.btn {
		width: 275px;
		height: 60px;
		/* padding: 0.5rem 1rem; */
		font-weight: 400;
		text-align: center;
		border: 1px solid transparent;
		background-image: url('$lib/assets/all/start_btn.webp');
	
		border-radius: 0.25rem;
		transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
	}
	.btn-text{
		-webkit-text-stroke: 1px #70158F;
		color: white;
	    font-weight: bold;
		font-size: 30px;
	}

	.light {
		background-color: #F8FDFF;
		color: #004A93;
	}

	.dark, .primary {
		background-color: #004A93;
		color: #ffffff;
	}

	.secondary {
		background-color: #FFD700;
		color: #004A93;
	}

	.info, .success {
		background-color: #0074E4;
		color: #ffffff;
	}

	.warning {
		background-color: #FF6700;
		color: #ffffff;
	}

	.danger {
		background-color: #EF3E42;
		color: #ffffff;
	}

	.btn:hover {
		opacity: 0.9;
	}

	.disabled, .disabled:hover {
		cursor: not-allowed;
		opacity: 0.65;
	}
</style>

<div class=""  >
{#if href}
	<a
		{href}
		{target}
		class=" text-[#003FA7] dark:text-white font-bold text-4xl flex items-center gap-2"
		class:disabled={disabled}
		on:click
	>
		<slot />
	</a>
{:else}
	<button 
	
		{disabled}
		class="  text-[#003FA7] dark:text-white  font-bold text-4xl flex items-center gap-2"
		
		class:disabled={disabled}
		on:click
	>
		<slot />
	</button>

	{/if}
</div>
