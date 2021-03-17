<script>
	import Router from "./router/Router.svelte";
	import NotFound from "./router/NotFound.svelte";

	export let name;
</script>

<main>
	<h1>Hello {name}!</h1>
	<p>Visit the <a href="https://svelte.dev/tutorial">Svelte tutorial</a> to learn how to build Svelte apps.</p>

	<Router>
		<NotFound>
			<h2>Page not found</h2>
		</NotFound>
	</Router>
</main>

<style lang="scss" global>
	@import "./main";

	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>