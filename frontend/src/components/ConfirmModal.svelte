<script>
  import { Modal } from "bootstrap";
  import { onMount } from "svelte";

  export let open = false;
  export let title;
  export let body;
  export let closeText;
  export let closeStyle = "btn-outline-secondary";
  export let confirmText;
  export let confirmStyle = "btn-primary";
  export let onConfirm = () => {};

  let modalElement;
  let modal = null;
  onMount(() => modal = new Modal(modalElement));

  const close = () => open = false;
  $: if (modal !== null) open ? modal.show() : modal.hide();
</script>

<div class="modal fade" id="confirm-modal" tabindex="-1" aria-labelledby="confirm-modal-label" aria-hidden="true" bind:this={modalElement} on:hide.bs.modal={close}>
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="confirm-modal-label">{@html title}</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" on:click={close}></button>
      </div>
      <div class="modal-body">
        <p>{@html body}</p>
      </div>
      <div class="modal-footer">
        <button type="button" class={`btn ${closeStyle}`} data-bs-dismiss="modal" on:click={close}>{closeText}</button>
        <button type="button" class={`btn ${confirmStyle}`} data-bs-dismiss="modal" on:click={onConfirm}>{confirmText}</button>
      </div>
    </div>
  </div>
</div>
