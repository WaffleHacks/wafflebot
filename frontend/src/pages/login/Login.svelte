<style lang="scss">
  .pt-30vh {
    padding-top: 30vh;
  }
</style>

<script>
  // An error message to be displayed
  export let message;

  // Redirect to server-side login through OAuth
  const redirect = () => (window.location.href = "/authentication/login");

  // Add the error from the query params if present
  const params = new URLSearchParams(window.location.search);
  const errorCode = params.get("error");
</script>

<svelte:head>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>WaffleBot | Login</title>
</svelte:head>

<div class="text-center pt-30vh">
  <h1 class="mb-4"><b>WaffleBot</b></h1>

  <br>

  {#if params.has("error")}
    <p class="alert alert-danger" style="width: 25%; margin-left: 37.5%" role="alert">
      {#if errorCode === "access_denied"}
        The authorization request was denied.
      {:else if errorCode === "server_error" || errorCode === "temporarily_unavailable"}
        Discord was unable to process the authorization request. Please try again later.
      {/if}
    </p>
  {/if}

  {#if message !== ""}
    <p class="alert alert-danger" style="width: 25%; margin-left: 37.5%" role="alert">{message}</p>
  {/if}

  <br/>

  <button class="btn btn-lg btn-success" on:click={redirect}>Login</button>
</div>
