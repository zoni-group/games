<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	export let disabled = false;
	export let flex = false;

	export let href: undefined | string = undefined;
	export let target: undefined | string = '_self';
	export let theme: "light" | "dark" | "primary" | "secondary" | "info" | "success" | "warning" | "danger" = "primary";
</script>

<style>
	.btn {
		width: 100%;
		padding: 0.5rem 1rem;
		font-weight: 400;
		text-align: center;
		border: 1px solid transparent;
		border-radius: 0.25rem;
		transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
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

{#if href}
	<a
		{href}
		{target}
		class="btn {theme}"
		class:disabled={disabled}
		on:click
	>
		<slot />
	</a>
{:else}
	<button
		{disabled}
		class="btn {theme}"
		class:disabled={disabled}
		on:click
	>
		<slot />
	</button>
{/if}
