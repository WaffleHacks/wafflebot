<script context="module">
  import { writable } from "svelte/store";

  const routes = {};

  export const activeRoute = writable({});

  // Register route from component
  export const register = (route) => (routes[route.path] = route);
</script>

<script>
  import page from "page";
  import { onMount, onDestroy } from "svelte";

  // Expose properties
  export let disabled = false;
  export let basePath = undefined;

  // Set last active component
  const last = (route) => (ctx) =>
    ($activeRoute = { ...route, params: ctx.params });

  // Setup the router on initialization
  onMount(() => {
    for (let [path, route] of Object.entries(routes)) {
      page(path, ...route.middleware, last(route));
    }

    // Set the base path
    if (basePath) page.base(basePath);

    // Start the router
    page.start();
  });

  // Remove event handlers on unmount
  onDestroy(page.stop);
</script>

<!-- Don't render anything if disabled -->
{#if !disabled}
  <slot/>
{/if}
