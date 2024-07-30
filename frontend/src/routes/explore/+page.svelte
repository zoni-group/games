<script lang="ts">
    import { getLocalization } from '$lib/i18n';
    const { t } = getLocalization();
    import SearchCard from '$lib/search-card.svelte';
    import { onMount } from 'svelte';

    let search_term = '';
    let resp_data = null;

    const submit = async () => {
        try {
            const res = await fetch('/api/v1/search/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    q: search_term,
                    attributesToHighlight: ['*']
                })
            });

            if (res.ok) {
                const resp_data_temp = await res.json();
                // Ensure resp_data is properly formatted
                resp_data = resp_data_temp.hits || [];
            } else {
                console.error('Error!', res.status);
            }
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    onMount(() => {
        submit();
    });
</script>

<svelte:head>
    <title>Zoni® AI - Search</title>
</svelte:head>

{#if resp_data !== null}
    {#if resp_data.length !== 0}
        <div class="grid lg:grid-cols-3 grid-cols-1">
            {#each resp_data as quiz}
                <SearchCard quiz={quiz._formatted} />
            {/each}
        </div>
    {:else}
        <div class="flex justify-center">
            <h1 class="text-4xl text-white">{$t('search_page.nothing_here')}</h1>
        </div>
        <div class="flex justify-center">
            <p class="text-white">
                Not finding what you are looking for? Search on 
                <a
                    class="underline"
                    href="https://create.kahoot.it/search?query={search_term}&tags=test&filter=filter%3D1"
                    target="_blank">Kahoot!</a>
                and 
                <a href="/import" class="underline">import</a> it!
            </p>
        </div>
    {/if}
{/if}
