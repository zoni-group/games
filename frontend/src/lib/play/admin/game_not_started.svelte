<script lang="ts">
	import AudioPlayer from '$lib/play/audio_player.svelte';
	import ControllerCodeDisplay from '$lib/components/controller/code.svelte';
	import { getLocalization } from '$lib/i18n';
	import GrayButton from '$lib/components/buttons/gray.svelte';
	import { fade } from 'svelte/transition';
	import { toast } from '@zerodevx/svelte-toast';
	import { onMount } from 'svelte';
    import playBtn from "$lib/assets/all/play.svg";
    import playDark from "$lib/assets/all/play_dark.svg";
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
			if (!players.some((p) => p.username === player.username)) {
				players.push(player);
				toast.push(`${player.username} has joined!`);
			}
		});
	});
</script>

<div class="w-full flex flex-col justify-center items-center ">
	<div class="fixed top-0 left-0">
		<AudioPlayer bind:play={play_music} />
	</div>
	<div class=" text-center flex flex-col justify-center items-center" style="padding:20px;">
		<p class="mt-4 text-[#00529B] text-sm dark:text-white md:text-5xl">
			{$t('play_page.players_waiting', { count: players.length ?? 0 })}
		</p>
		<p class="text-[#0056BD] dark:text-white font-semibold text-sm md:text-xl mt-16" >Please use your phone camera to scan the QR code or visit https://ai.zoni.edu
		</p>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<p on:click={copyUrl} class="underline cursor-pointer text-[#0056BD] dark:text-white font-normal sm:mb-10 text-sm w-fit px-4 py-2 md:text-xl mb-3 rounded-xl"  >Copy URL</p>
		<div class=" flex flex-col justify-center items-center">
			<!-- svelte-ignore a11y-click-events-have-key-events -->
			 <div class="bg-[#EF3E42] rounded-xl  flex flex-col justify-center">
				 <img
					 on:click={() => (fullscreen_open = true)}
					 alt={$t('qr_code_to_join_the_game')}
					 src={`/api/v1/utils/qr/${game_pin}`}
					 class="sm:m-10 bg-[#E3ECF4] p-3 "
				 />
				
			 </div>
		</div>
		<!-- <button
				class="mt-2 mr-2 p-2 bg-gray-300 rounded"
				on:click={copyUrl}
			>
				Copy URL
			</button> -->
		<!-- <div class="w-5/6 text-center mx-auto">	
			<p class="mt-4 text-2xl">
				{@html $t('play_page.join_description', {
					url: `https://${window.location.host}/play`,
					pin: game_pin
				})}
			</p>
		</div> -->
	</div>
	
	<div class="flex flex-col items-center
	 justify-center md:mt-10 border-4 bg-[#00529B] border-[#003FA7]/50 shadow-[#003FA7]/50 shadow-lg dark:border-white dark:shadow-none rounded-xl  p-5">
		<p class="text-white dark:text-white text-sm md:text-xl">
			Join using the activity
		</p>
		<p class=" text-white dark:text-white font-bold text-sm md:text-xl">
			CODE: {game_pin}
		</p>
	</div>
	
	<div class="flex flex-row justify-center w-full mt-4 px-10 flex-wrap">
		{#if players.length > 0}
			{#each players as player}
				<div class="p-2 m-2  text-white bg-[#0056BD] dark:bg-[#0C81FF] bg-opacity-50 rounded hover:cursor-pointer">
					<!-- svelte-ignore a11y-click-events-have-key-events -->
					<span
						class="hover:line-through text-lg"
						on:click={() => {
							kick_player(player.username);
						}}>{player.username}</span>
				</div>
			{/each}
		{/if}
	</div>
	<div class="flex justify-center w-full sm:-mb-12 mt-3 -mb-12">
		<div 
		class="px-5 py-2 flex items-center justify-center gap-5 border-[#00EDFF] my-3 border-4 bg-gradient-to-r from-[#0056BD] dark:from-[#FFE500] from-0%  to-[#5436AB] dark:to-[#FFB800] to-100% leading-5 text-white dark:text-[#00529B] transition-colors duration-200 transform rounded-full hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
		
		 >
		 <img src="{playBtn}" class="block dark:hidden" alt="">
		 <img src="{playDark}" class="hidden dark:block" alt="">
			<GrayButton
				disabled={players.length < 1}
				on:click={() => {
					socket.emit('start_game', '');
				}}
				textColor="#fff"
				classes="text-[#fff] dark:text-[#00529B]"
				> 
				{$t('admin_page.start_game')}
			</GrayButton>
		</div>
	</div>
</div>

{#if fullscreen_open}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<div
		class="fixed top-0 left-0 z-50 w-screen min-h-screen bg-black bg-opacity-50 flex p-2"
		transition:fade={{ duration: 80 }}
		on:click={() => (fullscreen_open = false)}
	>
		<img
			alt={$t('qr_code_to_join_the_game')}
			src={`/api/v1/utils/qr/${game_pin}`}
			class="object-contain rounded m-auto md:w-1/2 w-full  bg-white"
		/>
	</div>
{/if}
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
</style>