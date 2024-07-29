<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	export let scores;

	export let question_results: Array<{
		username: string;
		answer: string;
		right: boolean;
		time_taken: number;
		score: number;
	}>;

	function sortObjectbyValue(obj) {
		const ret = {};
		Object.keys(obj)
			.sort((a, b) => obj[b] - obj[a])
			.forEach((s) => (ret[s] = obj[s]));
		return ret;
	}

	export let username;
	let score_by_username = {};

	if (JSON.stringify(scores) === '{}') {
		for (const i of question_results) {
			scores[i.username] = 0;
		}
	}

	$: console.log(score_by_username, scores, 'dieter');
	for (const i of question_results) {
		score_by_username[i.username] = i.score;
	}

	$: scores = sortObjectbyValue(scores);

	const do_sth = () => {
		for (const i of Object.keys(score_by_username)) {
			scores[i] = (score_by_username[i] ?? 0) + (scores[i] ?? 0);
		}
		scores = scores;
	};

	do_sth();
</script>

<div class="flex items-center justify-center min-h-screen p-4">
	<div class="flex flex-col items-center bg-white bg-opacity-70 rounded-lg p-8">
		<p class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl text-[#00529B] dark:text-[#00529B] mb-4">
			+{score_by_username[username] ?? '0'}
		</p>
		<p class="text-lg sm:text-xl md:text-2xl lg:text-3xl text-[#00529B] dark:text-[#00529B]">
			Total score: {scores[username] ?? '0'}
		</p>
	</div>
</div>
