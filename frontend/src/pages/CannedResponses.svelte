<script>
  import { Modal } from "bootstrap";
  import { icons } from "feather-icons";
  import { onMount } from "svelte";
  import { CannedResponse } from "../api";
  import ConfirmModal from "../components/ConfirmModal.svelte";
  import FormModal from "../components/FormModal.svelte";
  import VariableFieldsInput from "../components/VariableFieldsInput.svelte";
  import { SVG_ATTRS } from "../constants";
  import { redirect } from "../router";
  import { CannedResponse as validate } from "../validators";

  // List state
  let responses = [];

  // States for create, delete, and edit modals
  let createModal = { key: "", title: "", content: "", fields: [], open: false };
  let deleteModal = { id: -1, key: "", open: false };
  let editModal = { id: -1, key: "", title: "", content: "", fields: [], open: false };

  // Form validation for create and edit modals
  let createResult = validate.get();
  let createErrors = {};
  let editResult = validate.get();
  let editErrors = {};

  onMount(async () => {
    // Enable the modals
    Array.from(document.querySelectorAll(".modal")).forEach(node => new Modal(node));

    // Get a list of the responses
    await refresh();
  });

  // Refresh the list of canned responses
  async function refresh() {
    const content = await CannedResponse.list();
    if (!content.success) redirect("/login");
    else responses = content.data.sort((e1, e2) => e1.id > e2.id);
  }

  // Create a new canned response
  async function create() {
    const fields = Object.fromEntries(createModal.fields.map(f => [f.name, f.value]));
    await CannedResponse.create(createModal.key, createModal.title, createModal.content, fields);
    await refresh();

    // Reset the modal
    validate.reset();
    createErrors = {};
    createModal = { key: "", title: "", content: "", fields: [], open: false };
    createResult = validate.get();
  }

  // Edit a response
  async function edit() {
    const fields = Object.fromEntries(editModal.fields.map(f => [f.name, f.value]));
    await CannedResponse.update(editModal.id, editModal.key, editModal.title, editModal.content, fields);
    await refresh();

    // Reset the modal
    editErrors = {};
    editResult = validate.get();
  }

  // Delete a response
  async function deleteResponse() {
    await CannedResponse.delete(deleteModal.id);
    await refresh();
  }

  const checkCreate = ({ target: { name } }) => validateCreate(name);
  const validateCreate = name => {
    createResult = validate(createModal, name);
    createErrors = createResult.getErrors();
  };

  const checkEdit = ({ target: { name } }) => validateEdit(name);
  const validateEdit = name => {
    editResult = validate(editModal, name);
    editErrors = editResult.getErrors();
  };
</script>

<h2 class="mt-3">Canned Responses</h2>

<br/>

<button type="button" class="btn btn-primary" on:click={refresh}>
  {@html icons["refresh-cw"].toSvg(SVG_ATTRS)}
  &nbsp;Refresh
</button>
<button type="button" class="btn btn-success" on:click={() => createModal.open = true}>
  {@html icons.plus.toSvg(SVG_ATTRS)}
  &nbsp;Create
</button>

<br/><br/>

<div class="table-responsive">
  <table class="table table-striped table-hover">
    <thead>
      <tr>
        <th scope="col">ID</th>
        <th scope="col">Key</th>
        <th scope="col">Title</th>
        <th scope="col" class="text-end">Actions</th>
      </tr>
    </thead>
    <tbody>
    {#each responses as response}
      <tr>
        <th scope="row">{response.id}</th>
        <td>{response.key}</td>
        <td>{response.title}</td>
        <td class="text-end">
          <button type="button" class="btn btn-outline-secondary" title="Edit" data-bs-toggle="modal" data-bs-target="#edit-modal" on:click={() => editModal = {...response, fields: Object.entries(response.fields).map(([name, value]) => ({ name, value })), open: true}}>
            {@html icons.edit.toSvg(SVG_ATTRS)}
          </button>
          <button type="button" class="btn btn-outline-danger" title="Delete" on:click={() => deleteModal = {id: response.id, key: response.key, open: true}}>
            {@html icons["trash-2"].toSvg(SVG_ATTRS)}
          </button>
        </td>
      </tr>
    {:else}
      <tr>
        <td colspan="4">None added yet...</td>
      </tr>
    {/each}
    </tbody>
  </table>
</div>

<ConfirmModal
  title="Are you sure?"
  body={`Are you sure you want to delete <code>${deleteModal.key}</code>?`}
  closeText="Nevermind"
  closeStyle="btn-secondary"
  confirmText="Delete"
  confirmStyle="btn-outline-danger"
  onConfirm={deleteResponse}
  open={deleteModal.open}
/>

<FormModal
  title={`Editing <code>${editModal.key}</code>`}
  onSave={edit}
  open={editModal.open}
  disabled={editResult.hasErrors()}
>
  <div class="row g-2">
    <div class="col-md">
      <div class="form-floating">
        <input id="edit-key-input" type="text" class="form-control" placeholder="key" bind:value={editModal.key} on:input={checkEdit}/>
        <label for="edit-key-input">Key</label>
        {#if editErrors.key}
          {#each editErrors.key as error}
            <div class="form-text text-danger">{error}</div>
          {/each}
        {/if}
      </div>
    </div>
    <div class="col-md">
      <div class="form-floating">
        <input id="edit-title-input" type="text" class="form-control" placeholder="title" bind:value={editModal.title} on:input={checkEdit}/>
        <label for="edit-title-input">Title</label>
        {#if editErrors.title}
          {#each editErrors.title as error}
            <div class="form-text text-danger">{error}</div>
          {/each}
        {/if}
      </div>
    </div>
  </div>
  <br/>
  <div class="form-floating">
    <textarea class="form-control" placeholder="content" id="edit-content-input" style="height: 25vh" bind:value={editModal.content} on:input={checkEdit} aria-labelledby="edit-content-help"></textarea>
    <label for="edit-content-input">Content</label>
    <div id="edit-content-help" class="form-text">
      You can use
      <a
        href="https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-"
        target="_blank"
        rel="noreferrer"
      >
        Discord-flavored markdown
      </a>
      here.
    </div>
    {#if editErrors.content}
      {#each editErrors.content as error}
        <div class="form-text text-danger">{error}</div>
      {/each}
    {/if}
  </div>
  <br/>
  <VariableFieldsInput
    label="Fields"
    description="Optional fields to be displayed along with the description."
    bind:fields={editModal.fields}
    onInput={checkEdit}
    errors={editErrors.fields}
  />
</FormModal>

<FormModal
  title="New Canned Response"
  onSave={create}
  open={createModal.open}
  disabled={createResult.hasErrors()}
>
  <div class="row g-2">
    <div class="col-md">
      <div class="form-floating">
        <input id="create-key-input" type="text" class="form-control" placeholder="key" bind:value={createModal.key} on:input={checkCreate}/>
        <label for="create-key-input">Key</label>
        {#if createErrors.key}
          {#each createErrors.key as error}
            <div class="form-text text-danger">{error}</div>
          {/each}
        {/if}
      </div>
    </div>
    <div class="col-md">
      <div class="form-floating">
        <input id="create-title-input" type="text" class="form-control" placeholder="title" bind:value={createModal.title} on:input={checkCreate}/>
        <label for="create-title-input">Title</label>
        {#if createErrors.title}
          {#each createErrors.title as error}
            <div class="form-text text-danger">{error}</div>
          {/each}
        {/if}
      </div>
    </div>
  </div>
  <br/>
  <div class="form-floating">
    <textarea class="form-control" placeholder="content" id="create-content-input" style="height: 25vh" bind:value={createModal.content} on:input={checkCreate} aria-labelledby="create-content-help"></textarea>
    <label for="create-content-input">Content</label>
    <div id="create-content-help" class="form-text">
      You can use
      <a
        href="https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-"
        target="_blank"
        rel="noreferrer"
      >
        Discord-flavored markdown
      </a>
      here.
    </div>
    {#if createErrors.content}
      {#each createErrors.content as error}
        <div class="form-text text-danger">{error}</div>
      {/each}
    {/if}
  </div>
  <br/>
  <VariableFieldsInput
    label="Fields"
    description="Optional fields to be displayed along with the description."
    bind:fields={createModal.fields}
    onInput={checkCreate}
    errors={createErrors.fields}
  />
</FormModal>
