<script lang="ts">
	import AudioPlayer from '$lib/play/audio_player.svelte';
	import ControllerCodeDisplay from '$lib/components/controller/code.svelte';
	import { getLocalization } from '$lib/i18n';
	import GrayButton from '$lib/components/buttons/gray.svelte';
	import { fade } from 'svelte/transition';
	import { toast } from '@zerodevx/svelte-toast';
	import { onMount } from 'svelte';

	export let game_pin: string;
	export let players;
	export let socket;
	export let cqc_code: string;

	let fullscreen_open = false;
	const { t } = getLocalization();
	let play_music = false;

	if (cqc_code === 'null') {
		cqc_code = null;
	}

	const kick_player = (username: string) => {
		socket.emit('kick_player', { username: username });
		for (let i = 0; i < players.length; i++) {
			console.log(players[i].username, username);
			if (players[i].username === username) {
				players.splice(i, 1);
				break;
			}
		}
		players = players;
	};

	const copyUrl = () => {
		const url = `https://${window.location.host}/play?pin=${game_pin}`;
		navigator.clipboard.writeText(url).then(() => {
			toast.push('URL copied to clipboard! Share it!');
		});
	};

		
	onMount(() => {
		socket.on('player_joined', (player) => {
			players.push(player);
			toast.push(`${player.username} has joined!`);
		});
	});
</script>

<div class="w-full h-full">
	<AudioPlayer bind:play={play_music} />
	<div class="mt-12 text-center">
		<div class="relative">
			<!-- svelte-ignore a11y-click-events-have-key-events -->
			<img
				on:click={() => (fullscreen_open = true)}
				alt={$t('qr_code_to_join_the_game')}
				src={`/api/v1/utils/qr/${game_pin}`}
				class="block mx-auto w-1/2 dark:bg-white shadow-2xl rounded hover:cursor-pointer max-h-screen h-5/6"
			/>
		</div>
		<button
				class="mt-2 mr-2 p-2 bg-gray-300 rounded"
				on:click={copyUrl}
			>
				Copy URL
			</button>
		<div class="w-5/6 text-center mx-auto">	
			<p class="mt-4 text-2xl">
				{@html $t('play_page.join_description', {
					url: `https://${window.location.host}/play`,
					pin: game_pin
				})}
			</p>
		</div>
	</div>
	<div class="flex justify-center w-full mt-4">
		<div>
			<GrayButton
				disabled={players.length < 1}
				on:click={() => {
					socket.emit('start_game', '');
				}}
				>{$t('admin_page.start_game')}
			</GrayButton>
		</div>
	</div>
	<div class="flex justify-center mt-4">
		<p class="text-xl mt-4">
			{$t('play_page.players_waiting', { count: players.length ?? 0 })}
		</p>
	</div>
	<div class="flex flex-row w-full mt-4 px-10 flex-wrap">
		{#if players.length > 0}
			{#each players as player}
				<div class="p-2 m-2 border-2 border-[#004A93] rounded hover:cursor-pointer">
					<span
						class="hover:line-through text-lg"
						on:click={() => {
							kick_player(player.username);
						}}>{player.username}</span>
				</div>
			{/each}
		{/if}
	</div>
</div>

{#if fullscreen_open}
	<div
		class="fixed top-0 left-0 z-50 w-screen h-screen bg-black bg-opacity-50 flex p-2"
		transition:fade={{ duration: 80 }}
		on:click={() => (fullscreen_open = false)}
	>
		<img
			alt={$t('qr_code_to_join_the_game')}
			src={`/api/v1/utils/qr/${game_pin}`}
			class="object-contain rounded m-auto h-full bg-white"
		/>
	</div>
{/if}
