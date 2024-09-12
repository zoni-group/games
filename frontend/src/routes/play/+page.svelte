<script lang="ts">
	import { socket } from '$lib/socket';
	import { browser } from '$app/environment';
	import JoinGame from '$lib/play/join.svelte';
	import { QuizQuestionType, type Answer, type Question as QuestionType } from '$lib/quiz_types';
	import ShowTitle from '$lib/play/title.svelte';
	import Question from '$lib/play/question.svelte';
	import { navbarVisible } from '$lib/stores';
	import ShowEndScreen from '$lib/play/admin/final_results.svelte';
	import KahootResults from '$lib/play/results_kahoot.svelte';
	import { getLocalization } from '$lib/i18n';
	import ZoniLogo from '$lib/components/zoniLogoPlay.svelte';

	const { t } = getLocalization();

	let disconnectedMessage = '';

	// Exports
	export let data;
	let { game_pin } = data;

	// Types
	interface GameMeta {
		started: boolean;
	}

	interface PlayerAnswer {
		username: string;
		answer: string;
		right: string;
	}

	let game_mode;
	let final_results: Array<null> | Array<Array<PlayerAnswer>> = [null];
	let question_index = '';
	let unique = {};
	navbarVisible.set(false);
	let game_pin_valid: boolean;
	let answer_results: Array<Answer>;
	let gameData;
	let solution: QuestionType;
	let username = '';
	let scores = {};
	let gameMeta: GameMeta = { started: false };
	let question;
	let preventReload = true;

	// Define the restart function that resets the game state
	function restart() {
		unique = {};
		question_index = '';
		answer_results = undefined;
	}

	// Functions for handling game state persistence using localStorage
	function storeState() {
		const state = {
			game_pin,
			username,
			question_index,
			gameMeta,
			gameData,
			scores,
			answer_results,
			final_results,
			game_mode,
			question,
			solution
		};
		localStorage.setItem('game_state', JSON.stringify(state));
		console.log('State saved:', state);
	}

	function restoreState() {
		const savedState = localStorage.getItem('game_state');

		if (savedState) {
			const {
				game_pin: storedGamePin,
				username: storedUsername,
				question_index: storedQuestionIndex,
				gameMeta: storedGameMeta,
				gameData: storedGameData,
				scores: storedScores,
				answer_results: storedAnswerResults,
				final_results: storedFinalResults,
				game_mode: storedGameMode,
				question: storedQuestion,
				solution: storedSolution,
			} = JSON.parse(savedState);

			// Compare URL game_pin with stored game_pin
			console.log('Compare Game Pin:', game_pin, storedGamePin);
			if (game_pin !== storedGamePin) {
				// If pins don't match, clear the state and allow the user to start a new session
				clearState();
				game_pin = ''; // Clear the game_pin so the user can enter a new one
				username = '';  // Reset username and other states
				question_index = '';
				gameMeta = { started: false };
				answer_results = undefined;
				final_results = [null];
				game_mode = '';
				return;
			}

			// If pins match, restore the stored state
			game_pin = storedGamePin || game_pin;
			username = storedUsername || username;
			question_index = storedQuestionIndex || question_index;
			gameMeta = storedGameMeta || gameMeta;
			gameData = storedGameData || gameData;
			scores = storedScores || scores;
			answer_results = storedAnswerResults || answer_results;
			final_results = storedFinalResults || final_results;
			game_mode = storedGameMode || game_mode;
			question = storedQuestion || question;
			solution = storedSolution || solution;

			// Retrieve the stored socket ID and emit rejoin event
			const storedSocketId = localStorage.getItem('socket_id');
			if (storedSocketId) {
				socket.emit('rejoin_game', {
					old_sid: storedSocketId,  // Use the stored Socket ID
					username: storedUsername,
					game_pin: storedGamePin,
				});
			}
		}
	}

	function clearState() {
		localStorage.removeItem('game_state');
		localStorage.removeItem('socket_id');
	}

	// Restore game state on load
	if (browser) {
		restoreState();
	}

	const confirmUnload = () => {
		if (preventReload) {
			event.preventDefault();
			event.returnValue = '';
			storeState(); // Ensure state is saved before reload
		}
	};

	// Socket events for managing the game connection and state
	socket.on('time_sync', (data) => {
		socket.emit('echo_time_sync', data);
	});

	socket.on('connect', async () => {
		console.log('Connected!');
		localStorage.setItem('socket_id', socket.id);  // Store the current Socket ID
		restoreState(); // Restore the state from localStorage if present
		const savedState = localStorage.getItem('game_state');
		if (savedState) {
			const { game_pin: savedGamePin, username: savedUsername } = JSON.parse(savedState);
			// Rejoin the game automatically with saved session data
			socket.emit('rejoin_game', { old_sid: socket.id, username: savedUsername, game_pin: savedGamePin });
		}
	});

	socket.on('joined_game', (data) => {
		gameData = data;
		game_mode = data.game_mode;
		storeState();  // Save state after joining the game
	});

	socket.on('rejoined_game', (data) => {
		console.log('Game rejoined successfully!');
		gameData = data;
		if (data.started) {
			gameMeta.started = true;
		}
		storeState();  // Store state after rejoining
	});

	socket.on('game_not_found', () => {
		clearState();
		alert('Game session not found!');
		window.location.reload();
	});

	socket.on('set_question_number', (data) => {
		solution = undefined;
		restart();
		question = data.question;
		question_index = data.question_index;
		answer_results = undefined;
		storeState();  // Save state when the question index changes
	});

	socket.on('start_game', () => {
		gameMeta.started = true;
		storeState();
	});

	socket.on('question_results', (data) => {
		restart();
		answer_results = data;
		storeState();
	});

	socket.on('username_already_exists', () => {
		window.alert('Username already exists!');
	});

	socket.on('kick', () => {
		window.alert('You got kicked');
		preventReload = false;
		clearState();
		window.location.reload();
	});

	socket.on('disconnect_reason', (data) => {
		disconnectedMessage = data.reason;
	});

	socket.on('final_results', (data) => {
		final_results = data;
		clearState();  // Clear state when the game ends
	});

	socket.on('solutions', (data) => {
		solution = data;
		storeState();
	});

	let darkMode = false;
	if (browser) {
		darkMode = localStorage.theme === 'dark' ||
			(!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
	}

	let bg_color;
	$: bg_color = gameData ? gameData.background_color : (darkMode ? '#383838' : '#FFFFFF');
</script>

<svelte:window on:beforeunload={confirmUnload} />
<svelte:head>
	<title>Zoni® AI - Play</title>
</svelte:head>

<ZoniLogo />
<div class="flex flex-col h-screen overflow-hidden">
	<div class="flex-1 overflow-y-auto" class:text-black={bg_color}>
		<!-- Show Join Game component if the game hasn't started or user has no game data -->
		{#if !gameMeta.started && gameData === undefined}
			<JoinGame bind:game_pin bind:game_mode bind:username />
	
		<!-- Show Final Results if the game has ended and results are available -->
		{:else if JSON.stringify(final_results) !== JSON.stringify([null])}
			<ShowEndScreen bind:data={scores} show_final_results={true} bind:username />
	
		<!-- Show the Title if the game hasn't started yet and there's no question_index -->
		{:else if !gameMeta.started && question_index === ''}
			<ShowTitle
				bind:title={gameData.title}
				bind:description={gameData.description}
				bind:cover_image={gameData.cover_image}
			/>
	
		<!-- Show Current Question if the game is in progress and question_index is set -->
		{:else if gameMeta.started && gameData !== undefined && question_index !== '' && answer_results === undefined}
			{#key unique}
				<div class="text-[#00529B] dark:text-[#00529B]">
					<Question bind:game_mode bind:question bind:question_index bind:solution />
				</div>
			{/key}
	
		<!-- Show Results for the Question if answer results are available -->
		{:else if gameMeta.started && answer_results !== undefined}
			{#if answer_results === null}
				<div class="w-full flex justify-center">
					<h1 class="text-3xl">{$t('admin_page.no_answers')}</h1>
				</div>
			{:else}
			<div class="min-h-screen flex flex-col items-center justify-center" >
				{#if question.type != QuizQuestionType.VOTING}
					<div>
						<h2 class="text-center text-[#00529B] dark:text-[#fff] font-bold sm:text-3xl text-lg my-8">{$t('words.result', { count: 2 })}</h2>

					</div>
					{#key unique}
						<KahootResults
							bind:username
							bind:question_results={answer_results}
							bind:scores
						/>
					{/key}
				{:else}
				<div>
					<h2 class="text-center text-[#00529B] dark:text-[#fff] font-bold sm:text-3xl text-lg my-8">Nice progress! Let’s continue</h2>
				</div>
				{/if}
			</div>

			{/if}
		{/if}
	</div>	
</div>
