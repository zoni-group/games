<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
    // import { alertModal } from '$lib/stores';
    import { captcha_enabled } from '$lib/config';
    import { browser } from '$app/environment';
    import { fade } from 'svelte/transition';
    import Spinner from '$lib/Spinner.svelte';
    import { onMount } from 'svelte';
    import { createTippy } from 'svelte-tippy';
    import { getLocalization } from '$lib/i18n';
    import playIcon from "$lib/assets/all/play.svg";

    const { t } = getLocalization();
    export let quiz_id;
    let captcha_selected = false;
    let selected_game_mode = 'kahoot';
    let loading = false;
    let custom_field = '';
    let cqcs_enabled = false;
    let randomized_answers = false;

    const tippy = createTippy({
        arrow: true,
        animation: 'perspective-subtle',
        placement: 'top-start',
        allowHTML: true
    });

    onMount(() => {
        const ls_data = localStorage.getItem('custom_field');
        custom_field = ls_data ? ls_data : '';
    });

    const start_game = async (id: string) => {
        let res;
        loading = true;
        localStorage.setItem('custom_field', custom_field);
        const cqcs_enabled_parsed = cqcs_enabled ? 'True' : 'False';
        const randomized_answers_parsed = randomized_answers ? 'True' : 'False';
        if (captcha_enabled && captcha_selected) {
            res = await fetch(
                `/api/v1/quiz/start/${id}?captcha_enabled=True&game_mode=${selected_game_mode}&custom_field=${custom_field}&cqcs_enabled=${cqcs_enabled_parsed}`,
                {
                    method: 'POST'
                }
            );
        } else {
            res = await fetch(
                `/api/v1/quiz/start/${id}?captcha_enabled=False&game_mode=${selected_game_mode}&custom_field=${custom_field}&cqcs_enabled=${cqcs_enabled_parsed}&randomize_answers=${randomized_answers_parsed}`,
                {
                    method: 'POST'
                }
            );
        }
        if (res.status !== 200) {
            alert('Starting game failed');
            window.location.assign('/account/login?returnTo=/dashboard');
        } else {
            const data = await res.json();
            // eslint-disable-next-line no-undef
            plausible('Started Game', { props: { quiz_id: id, game_id: data.game_id } });
            window.location.assign(
                `/admin?token=${data.game_id}&pin=${data.game_pin}&connect=1&cqc_code=${data.cqc_code}`
            );
        }
    };

    const on_parent_click = (e: Event) => {
        if (e.target !== e.currentTarget) {
            return;
        }
        quiz_id = null;
    };
    const close_start_game_if_esc_is_pressed = (key: KeyboardEvent) => {
        if (key.code === 'Escape') {
            quiz_id = null;
        }
    };
    onMount(() => {
        document.body.addEventListener('keydown', close_start_game_if_esc_is_pressed);
    });

    let darkMode = false;
	if (browser) {
		darkMode =
			localStorage.theme === 'dark' ||
			(!('theme' in localStorage) &&
				window.matchMedia('(prefers-color-scheme: dark)').matches);
	}

	let bg_color;
	$: bg_color = (darkMode ? '#ffffff' : '#FFFFFF');
</script>

<div
    class="fixed inset-0 flex justify-center items-center w-screen h-screen overflow-auto bg-black bg-opacity-60 z-50 py-5 "
    transition:fade={{ duration: 100 }}
    style="scrollbar-width: none;"
    on:click={on_parent_click}
	on:keydown={() => {}}
	on:keyup={() => {}}
	on:keypress={() => {}}
>
    <div
        class="w-5/6 dark:!bg-gray-600 m-auto rounded-lg shadow-lg p-4 flex flex-col "
        style="background-color: {bg_color}"
    >
        <div class="grid md:grid-cols-2 grid-cols-1 md:gap-16 gap-10 my-10">
            <div class=" flex flex-col items-center">
                <div
                class="rounded-xl bg-[#0056BD] xl:w-2/3 md:w-full text-white shadow-lg cursor-pointer transition-all p-5"
                class:opacity-50={selected_game_mode !== 'kahoot'}
                on:click={() => {
                    selected_game_mode = 'kahoot';
                }}
				on:keydown={() => {}}
				on:keyup={() => {}}
				on:keypress={() => {}}
            >
				<h2 class="text-center text-2xl flex items-center justify-center font-bold">
                    {$t('words.normal')}
                    <div class="flex items-center gap-2" >
                        <svg class="w-10 h-10 ml-8 mr--5 " xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><!--!Font Awesome Pro 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2024 Fonticons, Inc.--><path class="fa-secondary" opacity=".4" fill="#ffffff" d="M128 0C92.7 0 64 28.7 64 64V288H19.2C8.6 288 0 296.6 0 307.2C0 349.6 34.4 384 76.8 384H352V288H128V64H448V96h64V64c0-35.3-28.7-64-64-64H128zM576 448V192H448V448H576z"/><path class="fa-primary" fill="#ffffff" d="M448 192H576V448H448V192zm-16-64c-26.5 0-48 21.5-48 48V464c0 26.5 21.5 48 48 48H592c26.5 0 48-21.5 48-48V176c0-26.5-21.5-48-48-48H432z"/></svg>
                        
                        {#if selected_game_mode === 'kahoot'}
                            <svg
                                class="w-6 h-6 mr-2 "
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                                xmlns="http://www.w3.org/2000/svg"
                            >
                                <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M5 13l4 4L19 7"
                                ></path>
                            </svg>
                        {/if}

                    </div>
				</h2>
                </div>
                <p class="text-[#00529B] mt-3 text-sm xl:w-2/3 md:w-full text-center font-semibold dark:text-[#fff]">
                    {$t('start_game.normal_mode_description')}
                </p>
            </div>
            <div class=" flex flex-col items-center">
                <div
                    class="rounded-lg bg-[#007CDB] xl:w-2/3 md:w-full text-white shadow-lg cursor-pointer transition-all p-5"
                    class:opacity-50={selected_game_mode !== 'normal'}
                    on:click={() => {
                        selected_game_mode = 'normal';
                    }}
                    on:keydown={() => {}}
                    on:keyup={() => {}}
                    on:keypress={() => {}}
                >
                    <h2 class="text-center text-2xl flex items-center justify-center font-bold">
                        {$t('start_game.old_school_mode')}
                        <div class="flex items-center gap-2" >
                        <svg class="w-10 h-10 ml-8 mr--5 float-right" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--!Font Awesome Pro 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2024 Fonticons, Inc.--><path class="fa-secondary" opacity=".4" fill="#ffffff" d="M64 0C28.7 0 0 28.7 0 64V352c0 35.3 28.7 64 64 64H512c35.3 0 64-28.7 64-64V64c0-35.3-28.7-64-64-64H64zM512 64V288H64V64H512z"/><path class="fa-primary" fill="#ffffff" d="M512 64H64V288H512V64zM416 448H346.7L336 416H240l-10.7 32H160c-17.7 0-32 14.3-32 32s14.3 32 32 32H416c17.7 0 32-14.3 32-32s-14.3-32-32-32z"/></svg>
                            
                            {#if selected_game_mode === 'normal'}
                                <svg
                                    class="w-6 h-6 mr-2 float-right"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                    xmlns="http://www.w3.org/2000/svg"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M5 13l4 4L19 7"
                                    ></path>
                                </svg>
                            {/if}
                        </div>
                    </h2>
                </div>
                
                <p class="text-[#00529B] mt-3 xl:w-2/3 md:w-full text-sm text-center font-semibold dark:text-[#fff]">
                    {$t('start_game.old_school_mode_description')}
                </p>

            </div>
        </div>
        <div class="flex justify-center w-full my-auto">
            <label
                for="randomized-answers-toggle"
                class="inline-flex relative items-center cursor-pointer"
            >
                <input
                    type="checkbox"
                    bind:checked={randomized_answers}
                    id="randomized-answers-toggle"
                    class="sr-only peer"
                />
                <span
                    class="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-200 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"
                />
                <span class="ml-3 text-sm font-medium text-gray-900 font-semibold dark:text-white"> Randomize answers</span>
            </label>
        </div>
        <button 
        on:click={() => start_game(quiz_id)}
        class="flex bg-gradient-to-r from-[#0056B3] -mb-10 mt-4 mx-auto items-center justify-center gap-3 font-bold style-text md:text-2xl transition-all   via-[#0C81FF] to-[#0056B3] px-7 py-2 rounded-full border-4 border-[#0C81FF]"
    >
        <img src="{playIcon}" alt="">
        {$t('start_game.start_game')}
        </button>
        <!-- <button
            class="flex items-center hidden -mb-12 mt-4 mx-auto bg-lime-600 text-white p-4 rounded-lg shadow-lg hover:bg-lime-500 transition-all text-2xl"
            on:click={() => start_game(quiz_id)}
        >
			<svg class="w-12 h-12 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"> -->
                <!--!Font Awesome Pro 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2024 Fonticons, Inc.-->
                <!-- <path class="fa-secondary" opacity="1" fill="#ffffff" d="M96 48c0-8.8 7.2-16 16-16h32c8.8 0 16 7.2 16 16V64h48c8.8 0 16 7.2 16 16v48H352V80c0-8.8 7.2-16 16-16h48V48c0-8.8 7.2-16 16-16h32c8.8 0 16 7.2 16 16V80c0 8.8-7.2 16-16 16H416v32 32h48c8.8 0 16 7.2 16 16v48h32V144c0-8.8 7.2-16 16-16h32c8.8 0 16 7.2 16 16V272c0 8.8-7.2 16-16 16H512v80c0 8.8-7.2 16-16 16H448v80c0 8.8-7.2 16-16 16H384 336c-8.8 0-16-7.2-16-16V432c0-8.8 7.2-16 16-16h48V384H192v32h48c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H192 144c-8.8 0-16-7.2-16-16V384H80c-8.8 0-16-7.2-16-16V288H16c-8.8 0-16-7.2-16-16V144c0-8.8 7.2-16 16-16H48c8.8 0 16 7.2 16 16v80H96V176c0-8.8 7.2-16 16-16h48V128 96H112c-8.8 0-16-7.2-16-16V48zm64 192v64c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V240c0-8.8-7.2-16-16-16H176c-8.8 0-16 7.2-16 16zm192 0v64c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V240c0-8.8-7.2-16-16-16H368c-8.8 0-16 7.2-16 16z"/><path class="fa-primary" opacity="0.4" fill="#ffffff" d="M176 224c-8.8 0-16 7.2-16 16v64c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V240c0-8.8-7.2-16-16-16H176zm192 0c-8.8 0-16 7.2-16 16v64c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V240c0-8.8-7.2-16-16-16H368z"/></svg>
            {#if loading}
                <Spinner my_20={false} />
            {:else}
                {$t('start_game.start_game')}
            {/if}
        </button> -->

    </div>
</div>
<style>
	.style-text{
		-webkit-text-stroke: 1px #00529B;
		color: white;

		
	}
</style>