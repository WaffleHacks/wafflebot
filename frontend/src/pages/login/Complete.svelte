<style lang="scss">
  .pt-30vh {
    padding-top: 30vh;
  }
</style>

<script>
  import { onMount } from "svelte";
  import { User } from "../../api";
  import { redirect } from "../../router";
  import { user } from "../../stores";

  onMount(async function() {
    const content = await User.info();

    // Set the user's profile
    if (content.success) {
      user.set(content.data);
      redirect("/");

    // Redirect back to login if it failed for some reason
    } else redirect("/login");
  });
</script>

<div class="text-center pt-30vh">
  <h1>Logging you in...</h1>
  <h4 class="text-muted">You will be redirected shortly</h4>
</div>
