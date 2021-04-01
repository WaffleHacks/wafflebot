<script>
  import { icons } from "feather-icons";
  import { SVG_ATTRS } from "../constants";

  export let fields = [];
  export let label;
  export let description = "";
  export let errors = [];
  export let onInput = () => {};

  function addField() {
    // This is a hack to force svelte to notice an update
    // There's probably a better way to do it
    fields.push({});
    fields[fields.length - 1].name = "";
    fields[fields.length - 1].value = "";
  }

  const removeField = index => () => {
    // Remove the field
    fields = fields.filter((_, i) => i !== index);

    // Re-run validation
    setTimeout(onInput, 50);
  };
</script>

<div class="row g-2">
  <div class="col-2">
    <h6 class="mt-2">{label}</h6>
  </div>
  <div class="col-1">
    <button type="button" class="btn btn-sm" on:click={addField} on:click={onInput}>{@html icons['plus-circle'].toSvg(SVG_ATTRS)}</button>
  </div>
  <div class="form-text">{description}</div>
  {#if errors}
    {#each errors as error}
      <div class="form-text text-danger">{error}</div>
    {/each}
  {/if}
</div>

{#each fields as field, i}
  <div class="row mt-1">
    <div class="col-md">
      <div class="form-floating">
        <input id={`variable-field-name-${i}`} type="text" class="form-control" placeholder="variable-field" bind:value={fields[i].name} on:input={onInput}/>
        <label for={`variable-field-name-${i}`}>Name</label>
      </div>
    </div>
    <div class="col-md">
      <div class="form-floating">
        <input id={`variable-field-value-${i}`} type="text" class="form-control" placeholder="variable-field" bind:value={fields[i].value} on:input={onInput}/>
        <label for={`variable-field-value-${i}`}>Value</label>
      </div>
    </div>
    <div class="col-md-1">
      <button type="button" class="btn btn-sm" style="margin-top: 0.75rem" on:click={removeField(i)}>{@html icons['x-circle'].toSvg({ color: "red", ...SVG_ATTRS })}</button>
    </div>
  </div>
{/each}
