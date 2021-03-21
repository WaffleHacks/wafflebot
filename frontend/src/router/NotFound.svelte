<script>
  import { register, activeRoute } from "./Router.svelte";

  // Act as catch all handler
  export let path = "*";
  export let component = null;

  register({ path, component, middleware: [] });
</script>

{#if $activeRoute.path === path}
  <svelte:component this={component}/>
  <slot />
{/if}
