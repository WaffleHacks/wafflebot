<script>
	import { onMount } from "svelte";
	import { User } from "./api";
	import { Router, Route, NotFound, redirect } from "./router";
	import { user } from "./stores";

	import CannedResponses from "./pages/CannedResponses.svelte";
	import Home from "./pages/Home.svelte";
	import { Login, LoginComplete } from "./pages/login";
	import NotFoundPage from "./pages/NotFound.svelte";
	import Settings from "./pages/Settings.svelte";

	let authMessage = "";

	// Check that the user is logged in
	onMount(async function() {
	  // Fetch the user's profile
	  const content = await User.info();

	  // TODO: update eslint to fix improper indentation
	  if (content.success) user.set(content.data);
	  else {
	  	if (content.status === 403) authMessage = "You do not have permissions to access the panel!";
	  	redirect("/login");
	  }
	});
</script>

<main>
	<Router>
		<!-- General routes -->
		<Route component={Home}/>
		<Route path="/canned-responses" component={CannedResponses}/>
		<Route path="/settings" component={Settings}/>

		<!-- Authentication routes -->
		<Route path="/login" component={Login} layout={false} message={authMessage}/>
		<Route path="/login/complete" component={LoginComplete} layout={false}/>

		<!-- Catch all -->
		<NotFound component={NotFoundPage}/>
	</Router>
</main>

<style lang="scss" global>
	@import "./main";
</style>