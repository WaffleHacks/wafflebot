<script>
  import { Modal } from "bootstrap";
  import { onMount } from "svelte";

  export let open = false;
  export let title;
  export let disabled = false;
  export let onSave = () => {};

  let modalElement;
  let modal = null;
  onMount(() => modal = new Modal(modalElement));

  const close = () => open = false;
  $: if (modal !== null) open ? modal.show() : modal.hide();
</script>

<div class="modal fade" id="edit-modal" tabindex="-1" aria-labelledby="edit-modal-label" aria-hidden="true" bind:this={modalElement} on:hide.bs.modal={close}>
  <div class="modal-dialog modal-lg modal-fullscreen-sm-down">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="edit-modal-label">{@html title}</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" on:click={close}></button>
      </div>
      <div class="modal-body">
        <slot/>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal" on:click={close}>Cancel</button>
        <button type="button" class="btn btn-success" data-bs-dismiss="modal" on:click={onSave} {disabled}>Save</button>
      </div>
    </div>
  </div>
</div>