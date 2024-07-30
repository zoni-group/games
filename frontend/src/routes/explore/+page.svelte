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
    <title>Zoni® AI - Explore</title>
</svelte:head>

{#if resp_data !== null}
    {#if resp_data.length !== 0}
        <div class="grid lg:grid-cols-3 grid-cols-1">
            {#each resp_data as quiz}
                <SearchCard quiz={quiz._formatted} />
            {/each}
        </div>
    {/if}
{/if}
