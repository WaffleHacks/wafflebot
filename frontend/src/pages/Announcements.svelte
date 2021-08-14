<script>
  import { Modal } from "bootstrap";
  import { icons } from "feather-icons";
  import { DateTime } from "luxon";
  import { onMount } from "svelte";
  import { Announcements } from "../api";
  import ConfirmModal from "../components/ConfirmModal.svelte";
  import DateTimeInput from "../components/DateTimeInput.svelte";
  import FormModal from "../components/FormModal.svelte";
  import { SVG_ATTRS } from "../constants";
  import { redirect } from "../router";
  import { Announcement as validate } from "../validators";

  let announcements = [];

  // States for the modals
  let createModal = { name: "", send_at: "", content: "", title: null, embed: false, open: false };
  let deleteModal = { id: -1, name: "", open: false };
  let editModal = { id: -1, name: "", send_at: "", content: "", title: null, embed: false, open: false };

  // Form validation results
  let createResult = validate.get();
  let createErrors = {};
  let editResult = validate.get();
  let editErrors = {};

  onMount(async () => {
    Array.from(document.querySelectorAll(".modal")).forEach(node => new Modal(node));
    await refresh();
  });

  async function refresh() {
    const content = await Announcements.list();
    if (!content.success) redirect("/login");
    else announcements = content.data.sort((a, b) => a.id > b.id);
  }

  async function create() {
    await Announcements.create(createModal.name, createModal.send_at, createModal.embed, createModal.title, createModal.content);
    await refresh();

    validate.reset();
    createModal = { name: "", send_at: "", content: "", title: null, embed: false, open: false };
    createErrors = {};
    createResult = validate.get();
  }

  async function edit() {
    await Announcements.update(editModal.id, editModal.name, editModal.send_at, editModal.embed, editModal.title, editModal.content);
    await refresh();

    editErrors = {};
    editResult = validate.get();
  }

  async function deleteAnnouncement() {
    await Announcements.delete(deleteModal.id);
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

  // Convert to a operable object
  const timestamp = raw => DateTime.fromISO(raw);
</script>

<h2 class="mt-3">Announcements</h2>

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
        <th scope="col">When</th>
        <th scope="col">Name</th>
        <th scope="col" class="text-end">In embed?</th>
        <th scope="col" class="text-end">Actions</th>
      </tr>
    </thead>
    <tbody>
    {#each announcements as announcement}
      <tr>
        <th scope="row">{announcement.id}</th>
        <td>
          {#if timestamp(announcement.send_at).diffNow().as("seconds") < 0}
            <span class="badge bg-success">Sent</span>
          {/if}
          {timestamp(announcement.send_at).toLocaleString(DateTime.DATETIME_SHORT)}
        </td>
        <td>{announcement.name}</td>
        <td class="text-end">
          {#if announcement.embed}
            <span class="text-success">{@html icons["check-square"].toSvg(SVG_ATTRS)}</span>
          {:else}
            <span class="text-danger">{@html icons.square.toSvg(SVG_ATTRS)}</span>
          {/if}
        </td>
        <td class="text-end">
          <button type="button" class="btn btn-outline-secondary" title="Edit" data-bs-toggle="modal" data-bs-target="#edit-modal" on:click={() => editModal = { ...announcement, open: true } }>
            {@html icons.edit.toSvg(SVG_ATTRS)}
          </button>
          <button type="button" class="btn btn-outline-danger" title="Delete" on:click={() => deleteModal = { id: announcement.id, name: announcement.name, open: true } }>
            {@html icons["trash-2"].toSvg(SVG_ATTRS)}
          </button>
        </td>
      </tr>
    {:else}
      <tr>
        <td colspan="5">None added yet...</td>
      </tr>
    {/each}
    </tbody>
  </table>
</div>

<ConfirmModal
  title="Are you sure?"
  body={`Are you sure you want to delete <code>${deleteModal.name}</code>? This will cause permanent data loss.`}
  closeText="Nevermind"
  closeStyle="btn-secondary"
  confirmText="Delete"
  confirmStyle="btn-outline-danger"
  onConfirm={deleteAnnouncement}
  open={deleteModal.open}
/>

<FormModal
  title={`Editing <code>${editModal.name}</code>`}
  onSave={edit}
  open={editModal.open}
  disabled={editResult.hasErrors()}
>
  <div class="row g-2">
    <div class="col-md">
      <div class="form-floating">
        <input id="edit-name-input" type="text" class="form-control" placeholder="name" bind:value={editModal.name} on:input={checkEdit}/>
        <label for="edit-name-input">Name</label>
        {#if editErrors.key}
          {#each editErrors.key as error}
            <div class="form-text text-danger">{error}</div>
          {/each}
        {/if}
      </div>
    </div>
    <div class="col-md">
      <DateTimeInput bind:value={editModal.send_at} label="Sent at"/>
    </div>
  </div>
  <br/>
  <div class="form-floating">
    <textarea id="edit-content-input" class="form-control" placeholder="content" style="height: 25vh" bind:value={editModal.content} on:input={checkEdit}></textarea>
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
  <div class="row g-2">
    <div class="col-md-3">
      <div class="form-check form-switch mt-3 ms-2">
        <input id="edit-embed-input" class="form-check-input" type="checkbox" bind:checked={editModal.embed} on:input={checkEdit}/>
        <label class="form-check-label" for="edit-embed-input">Display in embed</label>
      </div>
    </div>
    <div class="col-md-9">
      <div class="form-floating">
        <input id="edit-title-input" type="text" class="form-control" placeholder="title" disabled={!editModal.embed} bind:value={editModal.title} on:input={checkEdit}/>
        <label for="edit-title-input">Embed Title</label>
        {#if editErrors.title}
          {#each editErrors.title as error}
            <div class="form-text text-danger">{error}</div>
          {/each}
        {/if}
      </div>
    </div>
  </div>
</FormModal>

<FormModal
  title="Create an announcement"
  onSave={create}
  open={createModal.open}
  disabled={createResult.hasErrors()}
>
  <div class="row g-2">
    <div class="col-md">
      <div class="form-floating">
        <input id="create-name-input" type="text" class="form-control" placeholder="name" bind:value={createModal.name} on:input={checkCreate}/>
        <label for="create-name-input">Name</label>
        {#if createErrors.key}
          {#each createErrors.key as error}
            <div class="form-text text-danger">{error}</div>
          {/each}
        {/if}
      </div>
    </div>
    <div class="col-md">
      <DateTimeInput bind:value={createModal.send_at} label="Sent at"/>
    </div>
  </div>
  <br/>
  <div class="form-floating">
    <textarea id="create-content-input" class="form-control" placeholder="content" style="height: 25vh" bind:value={createModal.content} on:input={checkCreate}></textarea>
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
  <div class="row g-2">
    <div class="col-md-3">
      <div class="form-check form-switch mt-3 ms-2">
        <input id="create-embed-input" class="form-check-input" type="checkbox" bind:checked={createModal.embed} on:input={checkCreate}/>
        <label class="form-check-label" for="create-embed-input">Display in embed</label>
      </div>
    </div>
    <div class="col-md-9">
      <div class="form-floating">
        <input id="create-title-input" type="text" class="form-control" placeholder="title" disabled={!createModal.embed} bind:value={createModal.title} on:input={checkCreate}/>
        <label for="create-title-input">Embed Title</label>
        {#if createErrors.title}
          {#each createErrors.title as error}
            <div class="form-text text-danger">{error}</div>
          {/each}
        {/if}
      </div>
    </div>
  </div>
</FormModal>
