<script lang="ts">
	import { onMount } from 'svelte';
	import { getLocalization } from '$lib/i18n';
	import { fly } from 'svelte/transition';
	import confetti from 'canvas-confetti';
	import FaCrown from 'svelte-icons/fa/FaCrown.svelte';
	import FinishingFlag from '$lib/components/FinishingFlag.svelte';
	import ZoniStar from '$lib/components/ZoniStar.svelte';
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
	<div class="min-h-screen flex flex-col items-center justify-center py-10">
		<canvas bind:this={canvas} class="absolute inset-0 w-full h-full pointer-events-none" />
		{#if data[username]}
			<div class="mt-16 flex justify-center w-full mb-6 z-10">
				<div class=" p-4 border-4 flex items-center border-[#00EDFF] rounded-lg shadow-lg bg-gradient-to-r from-[#0056BD] to-[#5436AB]">
					<FinishingFlag />
					<div class="w-2/3 m-auto" >
						<p class="text-center text-lg font-medium text-[#fff] dark:text-[#fff]">{$t('play_page.your_score', { score: data[username] })}</p>
						{#each player_names as player, i}
							{#if player === username}
								<p class="text-center text-[#FFE500] text-xl font-semibold mt-2">{$t('play_page.your_place', { place: i + 1 })}</p>
							{/if}
						{/each}
					</div>
				</div>
			</div>
		{/if}
		<div class="relative z-10 w-full max-w-3xl p-4 rounded-lg ">
			
			{#each player_names as player, i}
				{#if i <= player_count_or_five - 1}
					<div
						in:fly={{ y: -300, delay: player_count_or_five * 1200 - (i + 1) * 1000 }}
						class="flex items-center justify-between mb-4 p-4 rounded-lg  from-[#0056BD] bg-[#2082CD] to-[#002857] text-white" class:bg-gradient-to-r={i<3} class:border-4={player === username} class:border-yellow-400={player === username}
						style="font-size: {1.5 + (player_count_or_five - i) / 2}rem"
					>
						<div class="flex items-center justify-between w-full space-x-4">
							<div class="flex items-center space-x-6" >
								<p class="text-2xl font-semibold text-[#FFE500] " class:!text-white={i>=3} >{i+1}</p>
								<p>{player}</p>
							</div>
							<p>
								{#if i == 0}
								<ZoniStar />
								{/if}
							</p>
							<p>{data[player]}</p>
						</div>
					</div>
				{/if}
			{/each}
		</div>
	</div>
{/if}
