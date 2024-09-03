<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<svelte:head>
	<title>Zoni® AI/docs - Import from Kahoot</title>
	<meta
		name="description"
		content="How to import activities from KAHOOT! into Zoni AI, the open-source activity-application,  easily"
	/>
</svelte:head>
<article
	class="prose prose-sm sm:prose lg:prose-lg xl:prose-xl mx-auto mt-10 prose-slate px-4 dark:prose-invert"
>
	<h1 class="!text-[#0056BD] dark:!text-white">Import Activities from Kahoot into Zoni AI</h1>

	<p class="!text-[#0056BD] dark:!text-white">
		All in all, this procedure is pretty simple, so just go to <a
			href="https://create.kahoot.it/discover"
			rel="nofollow"
			target="_blank" class="!text-[#0056BD] dark:!text-white">create.kahoot.it/discover</a
		>, find the activity you want to import, click on it and copy the URL into your clipboard. Then
		go to
		<a href="/import" rel="nofollow" target="_blank" class="!text-[#0056BD] dark:!text-white">the import page</a>
		and paste the url into the text field.
	</p>

	<h2 class="!text-[#0056BD] dark:!text-white">Limitations</h2>
	<ul class="!text-[#0056BD] dark:!text-white">
		<li>Videos don't get imported</li>
		<li>Metadata doesn't get imported (Stuff like create-date, cover-image, etc.)</li>
		<li>Point-multipliers don't get imported</li>
	</ul>
</article>
