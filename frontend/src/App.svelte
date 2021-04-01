<script>
	import { onMount } from "svelte";
	import { User } from "./api";
	import { Router, Route, NotFound, redirect } from "./router";
	import { user } from "./stores";

	import CannedResponses from "./pages/CannedResponses.svelte";
	import { Login, LoginComplete } from "./pages/login";

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

		<Route path="/canned-responses" component={CannedResponses}/>

		<!-- Authentication routes -->
		<Route path="/login" component={Login} layout={false}/>
		<Route path="/login/complete" component={LoginComplete} layout={false}/>

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