<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import roundLogo from '$lib/assets/all/round_logo.webp';
	import roundLogoDark from '$lib/assets/all/dark_logo.webp';

	export let session_data;
	export let selected_method;
	export let done;
	export let step;

	const { t } = getLocalization();
	let isSubmitting;
	let password;

	const continue_in_login = async () => {
		if (!password) {
			return;
		}
		const res = await fetch(`/api/v1/login/step/1?session_id=${session_data.session_id}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ auth_type: 'PASSWORD', data: password })
		});
		if (res.status === 200) {
			done = true;
		} else if (res.status === 202) {
			step += 1;
			selected_method = null;
		} else if (res.status === 401) {
			let data;
			try {
				data = await res.json();
			} catch {
				alert("This shouldn't happen");
				window.location.reload();
			}
			if (data.detail === 'wrong credentials') {
				/*				alertModal.set({
					open: true,
					body: 'Please try again. Your email and or password were incorrect.',
					title: 'Wrong Credentials'
				});*/
				alert('Wrong credentials');
			}
		}
	};
</script>
<style lang="scss">
	:global(html.dark){
		.text-style{
			-webkit-text-stroke-color: white;
		}
	}
</style>
<div class="px-6 py-4">
	<div class="dark:hidden" >
		<img src="{roundLogo}" alt="Zoni Logo" class="mx-auto z-1 -mt-20">
	</div>
	<div class="hidden dark:block">
		<img src="{roundLogoDark}" alt="Zoni Logo" class="mx-auto z-1 -mt-20">
	</div>
	<h2 class="text-style my-5 dark:text-transparent">Zoni AI</h2>

	<form on:submit|preventDefault={continue_in_login}>
		<div class="w-full mt-4">
			<div class="dark:bg-transparent bg-white p-4 rounded-lg">
				<div class="relative bg-inherit w-full">
					<input
						id="password"
						bind:value={password}
						name="password"
						type="password"
						class="py-3 px-3 input-style"
						placeholder={$t('words.password')}
						autocomplete="current-password"
					/>
					<!-- <label
						for="password"
						class="absolute cursor-text left-0 -top-3 text-sm text-gray-700 dark:text-white bg-inherit mx-1 px-1 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-500 peer-placeholder-shown:top-2 peer-focus:-top-3 peer-focus:text-sky-600 peer-focus:text-sm transition-all"
					>
						{$t('words.password')}
					</label> -->
				</div>
			</div>
			<div class="flex items-center justify-center mt-4">
				
				<button
				class="px-5 py-2 border-[#00EDFF] my-3 border-4 bg-gradient-to-r from-[#0056BD] dark:from-[#FFE500] from-0%  to-[#5436AB] dark:to-[#FFB800] to-100% leading-5 text-white dark:text-[#00529B] font-semibold transition-colors duration-200 transform rounded-full hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
					disabled={!password}
					type="submit"
				>
					{#if isSubmitting}
						<svg class="h-4 w-4 animate-spin mx-auto" viewBox="3 3 18 18">
							<path
								class="fill-black"
								d="M12 5C8.13401 5 5 8.13401 5 12C5 15.866 8.13401 19 12 19C15.866 19 19 15.866 19 12C19 8.13401 15.866 5 12 5ZM3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12Z"
							/>
							<path
								class="fill-blue-100"
								d="M16.9497 7.05015C14.2161 4.31648 9.78392 4.31648 7.05025 7.05015C6.65973 7.44067 6.02656 7.44067 5.63604 7.05015C5.24551 6.65962 5.24551 6.02646 5.63604 5.63593C9.15076 2.12121 14.8492 2.12121 18.364 5.63593C18.7545 6.02646 18.7545 6.65962 18.364 7.05015C17.9734 7.44067 17.3403 7.44067 16.9497 7.05015Z"
							/>
						</svg>
					{:else}
						{$t('words.continue')}
					{/if}
				</button>
			</div>
			<div class="flex items-end w-full  flex-col justify-between mt-4" >
				<button
						on:click={() => {
							selected_method = 'BACKUP';
						}}
						class="text-sm text-[#00529B] dark:text-white underline"
						>{$t('login_page.use_backup_code')}</button
					>
			</div>
		</div>
	</form>
</div>
