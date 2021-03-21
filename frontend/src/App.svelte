<script>
	import { onMount } from "svelte";
	import { User } from "./api";
	import { Login, LoginComplete } from "./pages/login";
	import { Router, Route, NotFound, redirect } from "./router";
	import { user } from "./stores";

	// Check that the user is logged in
	onMount(async function() {
	  // Fetch the user's profile
	  const content = await User.info();

	  // TODO: update eslint to fix improper indentation
  if (content.success) user.set(content.data);
  else redirect("/login");
});
</script>

<main>
	<Router>
		<Route>
			<h2>Home Page</h2>
			<a href="/testing">Link</a>
		</Route>

		<!-- Authentication routes -->
		<Route path="/login" component={Login}/>
		<Route path="/login/complete" component={LoginComplete}/>

		<!-- Catch all -->
		<NotFound>
			<!-- TODO: add proper page not found -->
			<h2>Page not found</h2>
		</NotFound>
	</Router>
</main>

<style lang="scss" global>
	@import "./main";
</style>