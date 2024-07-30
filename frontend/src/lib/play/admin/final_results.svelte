<script lang="ts">
	import { onMount } from 'svelte';
	import { getLocalization } from '$lib/i18n';
	import { fly } from 'svelte/transition';
	import confetti from 'canvas-confetti';
	import FaCrown from 'svelte-icons/fa/FaCrown.svelte';

	const { t } = getLocalization();

	export let data;
	export let username;
	export let show_final_results: boolean;

	function sortObjectbyValue(obj) {
		const ret = {};
		Object.keys(obj)
			.sort((a, b) => obj[b] - obj[a])
			.forEach((s) => (ret[s] = obj[s]));
		return ret;
	}

	$: data = sortObjectbyValue(data);
	$: console.log(data, 'sorted, final');

	let player_names;
	$: player_names = Object.keys(data).sort((a, b) => data[b] - data[a]);

	let player_count_or_five;
	$: player_count_or_five = player_names.length >= 5 ? 5 : player_names.length;

	let canvas;
	onMount(() => {
		setTimeout(() => {
			confetti.create(canvas, {
				resize: true,
				useWorker: true
			});
			confetti({ particleCount: 200, spread: 160 });
		}, player_count_or_five * 1200 - 800);
	});
</script>

{#if show_final_results}
	<div class="min-h-screen flex flex-col items-center justify-center py-8">
		<canvas bind:this={canvas} class="absolute inset-0 w-full h-full pointer-events-none" />
		<div class="relative z-10 w-full max-w-3xl p-4 bg-white rounded-lg shadow-lg">
			{#each player_names as player, i}
				{#if i <= player_count_or_five - 1}
					<div
						in:fly={{ y: -300, delay: player_count_or_five * 1200 - (i + 1) * 1000 }}
						class="flex items-center justify-between mb-4 p-4 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 text-white"
						style="font-size: {1.5 + (player_count_or_five - i) / 2}rem"
					>
						<div class="flex items-center space-x-4">
							{#if i === 0}
								<FaCrown class="text-yellow-300 text-3xl" />
							{/if}
							<p class="font-bold">
								{$t('play_page.final_result_rank', {
									place: i + 1,
									username: player,
									points: data[player]
								})}
							</p>
						</div>
					</div>
				{/if}
			{/each}
		</div>
		{#if data[username]}
			<div class="fixed bottom-0 left-0 flex justify-center w-full mb-6 z-10">
				<div class="bg-white p-4 border-4 border-indigo-700 rounded-lg shadow-lg">
					<p class="text-center text-lg font-semibold text-indigo-700">{$t('play_page.your_score', { score: data[username] })}</p>
					{#each player_names as player, i}
						{#if player === username}
							<p class="text-center text-indigo-700 mt-2">{$t('play_page.your_place', { place: i + 1 })}</p>
						{/if}
					{/each}
				</div>
			</div>
		{/if}
	</div>
{/if}
