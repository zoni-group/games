<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script>
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	export let quiz;
	import ImportedOrNot from '$lib/view_quiz/imported_or_not.svelte';
</script>

<div class="flex justify-center  w-full mx-3 ">
	<a href="/view/{quiz.id}" class="sm:h-2/3 sm:w-2/3 w-full flex flex-col justify-center mx-3">
		<div class="  py-4 px-8 bg-white border-[#C0D8FF] border-2 shadow-lg shadow-[#C8DDFF] dark:shadow-none rounded-lg sm:my-15 my-10 dark:bg-[#0AEDFE] dark:bg-opacity-20">
			<!--			<div class='flex justify-center md:justify-end -mt-16'>
							<img class='w-20 h-20 object-cover rounded-full border-2 border-indigo-500'
								 src='https://images.unsplash.com/photo-1499714608240-22fc6ad53fb2?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80'>
						</div>-->
			<div>
				<div class="flex w-full items-center">
					<h2
						class="text-[#003FA7] dark:text-[#fff] text-3xl font-semibold truncate pr-2"
					>
						{@html quiz.title}
					</h2>
					<span class="inline-block ml-auto text-[#003FA7] dark:text-[#fff]">
						<ImportedOrNot imported={quiz.imported_from_kahoot} />
					</span>
				</div>
				<p
					class="mt-2 text-black dark:text-gray-300 break-all overflow-hidden text-ellipsis h-[4.5rem] block"
				>
					{@html quiz.description}
				</p>
			</div>
			<div class="flex mt-4 text-[#0060C5] dark:text-[#fff]">
				<span
					>{#if quiz.imported_from_kahoot === true}
						{$t('explore_page.imported_by')}
					{:else}
						{$t('explore_page.made_by')}
					{/if}
					{@html quiz.user}</span
				>
			</div>
		</div>
	</a>
</div>
