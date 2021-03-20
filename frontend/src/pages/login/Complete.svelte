<style lang="scss">
  .pt-30vh {
    padding-top: 30vh;
  }
</style>

<script>
  import { onMount } from "svelte";
  import { User } from "../../api";
  import { redirect } from "../../router";
  import { isAuthenticated, user } from "../../stores";

  onMount(() => {
    const controller = new AbortController();

    (async function () {
      try {
        // Fetch the user's profile
        const content = await User.info(controller.signal);

        // Save their info
        isAuthenticated.set(true);
        user.set(content.data);
      } catch (e) {
        // Mark the user as logged out
        isAuthenticated.set(false);
        user.set({});
      }

      // Go to the home page
      redirect("/");
    })();

    return () => controller.abort();
  });
</script>

<div class="text-center pt-30vh">
  <h1>Logging you in...</h1>
  <h4 class="text-muted">You will be redirected shortly</h4>
</div>
