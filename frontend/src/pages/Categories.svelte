<script>
  import { Modal } from "bootstrap";
  import { icons } from "feather-icons";
  import { onMount } from "svelte";
  import { Categories } from "../api";
  import ConfirmModal from "../components/ConfirmModal.svelte";
  import FormModal from "../components/FormModal.svelte";
  import { SVG_ATTRS } from "../constants";
  import { redirect } from "../router";

  let categories = [];
  let createField = "";
  let deleteModal = { id: -1, name: "", open: false };
  let editModal = { id: -1, name: "", open: false };

  onMount(async () => {
    // Enable the modals
    Array.from(document.querySelectorAll(".modal")).forEach(node => new Modal(node));

    // Get the categories
    await refresh();
  });

  // Refresh the list of categories
  async function refresh() {
    const content = await Categories.list();
    if (!content.success) redirect("/login");
    else categories = content.data;
  }

  // Create a new category
  async function create() {
    await Categories.create(createField);
    await refresh();

    // Reset the field
    createField = "";
  }

  // Edit a category
  async function edit() {
    await Categories.update(editModal.id, editModal.name);
    await refresh();

    // Reset the fields
    editModal = { id: -1, name: "", open: false };
  }

  // Delete a category
  async function deleteCategory() {
    await Categories.delete(deleteModal.id);
    await refresh();
  }
</script>


<h2 class="mt-3">Categories</h2>

<br/>

<button type="button" class="btn btn-primary" on:click={refresh}>
  {@html icons["refresh-cw"].toSvg(SVG_ATTRS)}
  &nbsp;Refresh
</button>

<br/><br/>

<div class="row">
  <div class="col-md-4">
    <div class="form-floating mb-3">
      <input type="text" class="form-control" id="create-category-name" placeholder="Category Name" bind:value={createField}/>
      <label for="create-category-name">Category Name</label>
    </div>
  </div>
  <div class="col-md-2">
    <button type="button" class="btn btn-outline-success" style="margin-top: 0.6rem" on:click={create}>
      {@html icons.plus.toSvg(SVG_ATTRS)}
      &nbsp;Add
    </button>
  </div>
</div>

<br/>

<!-- TODO: add link to a category's tickets -->

<div class="table-responsive">
  <table class="table table-striped table-hover">
    <thead>
      <tr>
        <th scope="col">ID</th>
        <th scope="col">Name</th>
        <th scope="col">Actions</th>
      </tr>
    </thead>
    <tbody>
    {#each categories as category}
      <tr>
        <th scope="row">{category.id}</th>
        <td>{category.name}</td>
        <td>
          <button type="button" class="btn btn-outline-secondary" title="Edit" on:click={() => editModal = {...category, open: true}}>
            {@html icons.edit.toSvg(SVG_ATTRS)}
          </button>
          <button type="button" class="btn btn-outline-danger" title="Delete" on:click={() => deleteModal = {...category, open: true}}>
            {@html icons["trash-2"].toSvg(SVG_ATTRS)}
          </button>
        </td>
      </tr>
    {/each}
    </tbody>
  </table>
</div>

<ConfirmModal
  title="Are you sure?"
  body={`Are you sure you want to delete the <code>${deleteModal.name}</code> category?`}
  closeText="Nevermind"
  closeStyle="btn-secondary"
  confirmText="Delete"
  confirmStyle="btn-outline-danger"
  onConfirm={deleteCategory}
  open={deleteModal.open}
/>

<FormModal
  title={`Editing <code>${editModal.name}</code>`}
  open={editModal.open}
  onSave={edit}
>
  <div class="form-floating">
    <input id="edit-name-input" type="text" class="form-control" placeholder="category name" bind:value={editModal.name}/>
    <label for="edit-name-input">Name</label>
  </div>
</FormModal>
