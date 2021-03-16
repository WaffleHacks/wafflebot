<script>
    import { register, activeRoute } from "./Router.svelte";

    // Define props
    export let path = "/";
    export let component = null;
    export let middleware = [];

    // Page.js params placeholder
    let params = {};

    // Register the route
    register({ path, component, middleware });

    $: if ($activeRoute.path === path) params = $activeRoute.params;
</script>

{#if $activeRoute.path === path}
    <!-- Prefer props over slots -->
    {#if $activeRoute.component}
        <svelte:component this={$activeRoute.component} {...$$restProps} {...params} />
    {:else}
        <slot {params} />
    {/if}
{/if}
