<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import socketManager from '$lib/socketManager';
	import NoSleep from 'nosleep.js';
	import { socket } from '$lib/socket';
	import { browser } from '$app/environment';
	import JoinGame from '$lib/play/join.svelte';
	import { QuizQuestionType, type Answer, type Question as QuestionType } from '$lib/quiz_types';
	import ShowTitle from '$lib/play/title.svelte';
	import Question from '$lib/play/question.svelte';
	import { navbarVisible } from '$lib/stores';
	import ShowEndScreen from '$lib/play/admin/final_results.svelte';
	import KahootResults from '$lib/play/results_kahoot.svelte';
	import { getLocalization, initLocalizationContext } from '$lib/i18n';
	import ZoniLogo from '$lib/components/zoniLogoPlay.svelte';
	import en from '$lib/i18n/locales/en.json';
	import { toast } from '@zerodevx/svelte-toast';
	const { t, currentLanguage } = getLocalization();

	let noSleep;
	let disconnectedMessage = '';
	// Exports
	export let data;
	let { game_pin } = data;
	let username = '';
	let game_mode = '';
	
	// Types
	interface GameMeta {
		started: boolean;
	}

	interface PlayerAnswer {
		username: string;
		answer: string;
		right: string;
	}

	let final_results: Array<null> | Array<Array<PlayerAnswer>> = [null];
	let question_index = '';
	let unique = {};
	navbarVisible.set(false);
	let game_pin_valid: boolean;
	let answer_results: Array<Answer>;
	let gameData;
	let solution: QuestionType;
	let scores = {};
	let gameMeta: GameMeta = { started: false };
	let question;
	let preventReload = true;
	let language;
	let acknowledgement = {
		answered: false,
		answer: '',
	};
	let selected_answer = '';
	let gameEnded = false;
	let hasRejoined = false;

	function handleTimeSync(data) {
		console.log('Time sync:', data);
		socket.emit('echo_time_sync', data);
	}

	function handleJoinedGame(data) {
		console.log('Joined game:', data);
		gameData = data;
		game_mode = data.game_mode;
		//selected_answer = '';

		if (data.question_show === false) {
			acknowledgement.answered = true;
		} else {
			acknowledgement.answered = false;
		}

		storeState();  // Save state after joining the game
	}

	function handleJoinedGameLate(data) {
		console.log('Joined game late:', data);
		checkFinalizedGame(game_pin);
		let converted_scores =  Object.fromEntries(Object.entries(data.player_scores).map(([key, value]) => [key, Number(value)])); // This statement converts string values to numbers in an object
		scores = converted_scores;
		console.log('scores', scores);
		
		gameData = data;
		game_mode = data.game_mode;
		gameMeta.started = true;  // Ensure the game state reflects that it's in progress

		if (data.question_show === false) {
			acknowledgement.answered = true;
		} else {
			acknowledgement.answered = false;
		}

		storeState();  // Store the current game state locally
	}

	function handleRejoinedGame(data) {
		console.log('Rejoined game:', data);
		checkFinalizedGame(game_pin);
		let converted_scores =  Object.fromEntries(Object.entries(data.player_scores).map(([key, value]) => [key, Number(value)])); // This statement converts string values to numbers in an object
		scores = converted_scores;
		console.log('scores', scores);

		game_mode = data.game_mode;

		console.log('Latest answer:', data.latest_answer);
		gameData = data;
		if (data.started) {
			gameMeta.started = true;
			question_index = data.current_question;  // Set current question
		}

		if (data.latest_answer) {
			if (data.latest_answer.question_index === question_index) {
				acknowledgement.answered = true;
				acknowledgement.answer = data.latest_answer.answer;
			} else {
				acknowledgement.answered = false;
			}
		} else {
			if (data.question_show === false) {
				acknowledgement.answered = true;
			} else {
				acknowledgement.answered = false;
			}
		}
		storeState();  // Store state after rejoining
	}

	function handleGameNotFound() {
		console.log('Game session not found!');
		clearState();
		alert('Game session not found!');
		window.location.reload();
	}

	function handleSetQuestionNumber(data) {
		console.log('Set question number:', data);
		solution = undefined;
		restart();
		question = data.question;
		question_index = data.question_index;
		answer_results = undefined;
		if (data.question_show === false) {
			acknowledgement.answered = true;
		} else {
			acknowledgement.answered = false;
		}
		acknowledgement.answer = '';
		selected_answer = '';
		window.scrollTo(0, 0);
		storeState();  // Save state when the question index changes
	}

	function handleStartGame() {
		console.log('Game started!');
		gameMeta.started = true;
		window.scrollTo(0, 0);
		storeState();
	}

	function handleQuestionResults(data) {
		console.log('Question results:', data);
		restart();
		answer_results = data;
		storeState();
	}

	function handleUsernameAlreadyExists() {
		console.log('Username already exists!');
		alert('Username already exists!');
	}

	function handleKick() {
		console.log('You got kicked');
		alert('You got kicked');
		preventReload = false;
		clearState();
		window.location.reload();
	}

	function handleDisconnectReason(data) {
		console.log('Disconnected:', data);
		disconnectedMessage = data.reason;
	}

	function handleFinalResults(data) {
		console.log('Final results:', data);
		final_results = data.results;
		let converted_scores =  Object.fromEntries(Object.entries(data.player_scores).map(([key, value]) => [key, Number(value)])); // This statement converts string values to numbers in an object
		scores = converted_scores;
		console.log('Final scores:', scores);
		gameEnded = true;
		clearState();  // Clear state when the game ends
		if (browser) {
			noSleep.disable(); // Disable wake lock when the game ends
		}
	}

	function handleSolutions(data) {
		console.log('Solutions:', data);
		solution = data;
		acknowledgement.answered = true;
		storeState();
	}

	// Restore game state on load
	onMount(() => {
		restoreState();
		checkFinalizedGame(game_pin);
		noSleep = new NoSleep(); // Create a NoSleep instance
		const enableNoSleep = () => {
			noSleep.enable(); // Enable wake lock to prevent the screen from locking
			window.removeEventListener('click', enableNoSleep);
		};

		// Add event listener to enable NoSleep on the first user interaction
		window.addEventListener('click', enableNoSleep);

		window.addEventListener('visibilitychange', handleVisibilityChange);
	});

	socketManager.addEventListener('disconnect', handleDisconnect);
	socketManager.addEventListener('connect', handleConnect);
	socketManager.addEventListener('time_sync', handleTimeSync);
	socketManager.addEventListener('joined_game', handleJoinedGame);
	socketManager.addEventListener('joined_game_late', handleJoinedGameLate);
	socketManager.addEventListener('rejoined_game', handleRejoinedGame);
	socketManager.addEventListener('game_not_found', handleGameNotFound);
	socketManager.addEventListener('set_question_number', handleSetQuestionNumber);
	socketManager.addEventListener('start_game', handleStartGame);
	socketManager.addEventListener('question_results', handleQuestionResults);
	socketManager.addEventListener('username_already_exists', handleUsernameAlreadyExists);
	socketManager.addEventListener('kick', handleKick);
	socketManager.addEventListener('disconnect_reason', handleDisconnectReason);
	socketManager.addEventListener('final_results', handleFinalResults);
	socketManager.addEventListener('solutions', handleSolutions);

	onDestroy(() => {
		if (browser) {
    		window.removeEventListener('visibilitychange', handleVisibilityChange);
		}
		console.log("Removing socket event listeners");
		socketManager.removeEventListener('disconnect', handleDisconnect);
		socketManager.removeEventListener('connect', handleConnect);
		socketManager.removeEventListener('time_sync', handleTimeSync);
		socketManager.removeEventListener('joined_game_late', handleJoinedGameLate);
		socketManager.removeEventListener('rejoined_game', handleRejoinedGame);
		socketManager.removeEventListener('game_not_found', handleGameNotFound);
		socketManager.removeEventListener('set_question_number', handleSetQuestionNumber);
		socketManager.removeEventListener('start_game', handleStartGame);
		socketManager.removeEventListener('question_results', handleQuestionResults);
		socketManager.removeEventListener('username_already_exists', handleUsernameAlreadyExists);
		socketManager.removeEventListener('kick', handleKick);
		socketManager.removeEventListener('disconnect_reason', handleDisconnectReason);
		socketManager.removeEventListener('final_results', handleFinalResults);
		socketManager.removeEventListener('solutions', handleSolutions);
	
  	});

	function handleConnect() {
    	console.log('Connected!');
		toast.push('Connected!', {
			theme: {
    			'--toastColor': 'mintcream',
    			'--toastBackground': 'rgba(72,187,120,0.9)',
    			'--toastBarBackground': '#2F855A'
  			}
		});
		localStorage.setItem('socket_id', socket.id);  // Store the current Socket ID
		//restoreState(); // Restore the state from localStorage if present
		const savedState = localStorage.getItem('game_state');
		if (savedState) {
			const { game_pin: savedGamePin, username: savedUsername } = JSON.parse(savedState);
			// Rejoin the game automatically with saved session data
			if (!hasRejoined) {
				hasRejoined = true;
				socket.emit('rejoin_game', { old_sid: socket.id, username: savedUsername, game_pin: savedGamePin });
			}
		} else {
			// Check if game already started and allow late joining
			if (gameMeta.started) {
				socket.emit('join_late', { sid: socket.id , username: username, game_pin: game_pin });

				// Rejoin logic, emitting a late join event if the game has already started
				// Use the fetchGameState function to get the game state
				fetchGameState(game_pin).then((gameState) => {
					if (gameState) {
						checkFinalizedGame(game_pin);
						gameData = gameState;
						game_mode = gameState.game_mode;
						if (gameState.started) {
							gameMeta.started = true;
							question_index = gameState.question_index;
							if (gameData.question_show === false) {
        						acknowledgement.answered = true;
        					} else {
								acknowledgement.answered = false;
							}
						}
					}
				});
				if (!hasRejoined) {
					hasRejoined = true;
					socket.emit('rejoin_game', { old_sid: socket.id, username: username, game_pin: game_pin });
				}
			}		
		}
  	}

	function handleDisconnect(reason) {
		hasRejoined = false;
    	console.log('Socket disconnected:', reason);
		toast.push('Connection lost. Attempting to reconnect...', {
  			theme: {
				'--toastColor': 'white',
				'--toastBackground': 'rgba(255,69,58,0.9)',
				'--toastBarBackground': '#FF453A'
  			}	
		});
  	}

	// Fetch game state in the browser
	async function fetchGameState(game_pin: string) {
		if (game_pin && /^\d{6}$/.test(game_pin)) {
			try {
			// Replace the URL with your actual backend URL
			const response = await fetch(`/api/v1/game_state/${game_pin}`);
			console.log('Fetch Game State Response:', response);

			if (!response.ok) {
				throw new Error(`Failed to fetch game state: ${response.statusText}`);
			}

			const gameState = await response.json();
			return gameState;
			} catch (error) {
				console.error('Error fetching game state:', error);
				return null;
			}
		}
	}

	// Define the restart function that resets the game state
	function restart() {
		unique = {};
		question_index = '';
		answer_results = undefined;
	}

	// Functions for handling game state persistence using localStorage
	function storeState() {
		if (!username || !game_pin || question_index === null || question_index === undefined || gameEnded) {
			return;
		}
		// Use URL `game_pin` from the `data` first
		if (data?.game_pin && /^\d{6}$/.test(data?.game_pin)) {
			game_pin = data?.game_pin;
			console.log('Store using Game Pin from URL:', game_pin);
		}
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
			solution,
			acknowledgement,
			selected_answer
		};
		localStorage.setItem('game_state', JSON.stringify(state));
		console.log('State saved:', state);
	}

	function restoreState() {
		const savedState = localStorage.getItem('game_state');

		// Use URL `game_pin` from the `data` first
		if (data?.game_pin && /^\d{6}$/.test(data?.game_pin)) {
			game_pin = data?.game_pin;
			console.log('Resore using Game Pin from URL:', game_pin);
		}

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
				acknowledgement: storedAcknowledgement,
				selected_answer: storedSelectedAnswer,
			} = JSON.parse(savedState);

			// Use storedGamePin if game_pin is undefined or empty
            if (!game_pin || game_pin === '') {
                game_pin = storedGamePin;
            }

			// Compare pins only if game_pin is defined
			if (game_pin && game_pin !== storedGamePin) {
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
			acknowledgement = storedAcknowledgement || acknowledgement;

			console.log('Stored Game Data:', storedGameData);
			selected_answer = storedSelectedAnswer || selected_answer;

			// Retrieve the stored socket ID and emit rejoin event
			const storedSocketId = localStorage.getItem('socket_id');
			if (!hasRejoined && storedSocketId) {
				hasRejoined = true;
				socket.emit('rejoin_game', {
					old_sid: storedSocketId,  // Use the stored Socket ID
					username: storedUsername,
					game_pin: storedGamePin,
				});
			}
			console.log('State restored:', savedState);
		}
	}

	function clearState() {
		localStorage.removeItem('game_state');
		localStorage.removeItem('socket_id');
	}

	function handleVisibilityChange() {
		if (document.visibilityState === 'visible') {
      		if (!socket.connected) {
				hasRejoined = false;
        		console.log('Attempting to reconnect...');
        		socket.connect();
      		}
    	}
	}

	function checkFinalizedGame(game_pin) {
		fetchGameState(game_pin).then((gameState) => {
			if (gameState) {
				if (gameState.current_question + 1 === gameState.question_count && gameState.question_show === false) {
					gameEnded = true;
					clearState();
					alert('This session has already ended.');
					window.location.href = '/play';
				}
			}
		});
	}

	// Socket events for managing the game connection and state

	let darkMode = false;
	if (browser) {
		darkMode = localStorage.theme === 'dark' ||
			(!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
	}

	let bg_color;
	$: bg_color = gameData ? gameData.background_color : (darkMode ? '#383838' : '#FFFFFF');
	
	$: language = gameData ? gameData.language_toggle : false;
	// $: console.log('Language:', language);
	
</script>

<svelte:window on:visibilitychange={handleVisibilityChange} />
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
			<ShowEndScreen bind:data={scores} bind:language show_final_results={true} bind:username />
	
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
					<Question bind:game_mode bind:question bind:question_index bind:solution bind:language bind:acknowledgement bind:selected_answer on:storeStateNeeded={storeState} on:restoreStateNeeded={restoreState}/>
				</div>
			{/key}
	
		<!-- Show Results for the Question if answer results are available -->
		{:else if gameMeta.started && answer_results !== undefined}
			{#if answer_results === null}
				<div class="w-full flex justify-center">
					<h1 class="text-3xl">
						{#if language}
						{en.admin_page.no_answers}
						{:else}
						{$t('admin_page.no_answers')}
						{/if}
					</h1>
				</div>
			{:else}
			<div class="min-h-screen flex flex-col items-center justify-center" >
				{#if question.type != QuizQuestionType.VOTING}
					<div>
						<h2 class="text-center text-[#00529B] dark:text-[#fff] font-bold sm:text-3xl text-lg my-8">
							{#if language}
								{en.words.result}
							{:else}
								{$t('words.result', { count: 2 })}
							{/if}
						</h2>
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
					<h2 class="text-center text-[#00529B] dark:text-[#fff] font-bold sm:text-3xl text-lg my-8">
						{#if language}
							 {en.admin_page.after_voting}
						{:else}
							{$t('admin_page.after_voting')}
						{/if}
					</h2>
				</div>
				{/if}
			</div>
			{/if}
		{/if}
	</div>	
</div>
