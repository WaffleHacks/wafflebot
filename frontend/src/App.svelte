<script>
	import { Router, Route, NotFound, redirect } from "./router";
	import { Login, LoginComplete } from "./pages/login";
	import { isAuthenticated } from "./stores";

	// Ensure the user is logged in for all routes
	const isLoggedIn = (ctx, next) => {
	  if ($isAuthenticated) next();
	  else redirect("/login");
	};
</script>

<main>
	<Router>
		<Route middleware={[isLoggedIn]}>
			<h2>Home Page</h2>
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