<script>
  import { icons } from "feather-icons";
  import { onMount } from "svelte";
  import { Settings } from "../api";
  import { SVG_ATTRS } from "../constants";
  import { redirect } from "../router";

  let settings = [];

  onMount(async () => await refresh());

  // Refresh the settings
  async function refresh() {
    const content = await Settings.list();
    if (!content.success) redirect("/login");
    else settings = content.data.map(setting => {
      // Convert the integers to strings for easy text input
      if (Array.isArray(setting.value)) setting.value = setting.value.map(v => v.toString());
      else setting.value = setting.value.toString();

      return setting;
    });
  }

  // Update a value
  const update = index => async () => {
    let setting = settings[index];
    await Settings.update(setting.key, setting.value);
    await refresh();
  };

  // Add an element to the values array
  const addArrayValue = setting => () => {
    // Add the element
    settings[setting].value.push("");

    // Trigger an update
    settings = settings;
  };

  // Remove an element from the values array
  const removeArrayValue = (setting, index) => () => {
    // Remove the element at the index
    settings[setting].value.splice(index, 1);

    // Trigger an update
    settings = settings;
  };
</script>

<h2 class="mt-3">Settings</h2>

<br/>

<button type="button" class="btn btn-primary" on:click={refresh}>
  {@html icons['refresh-cw'].toSvg(SVG_ATTRS)}
  &nbsp;Refresh
</button>

<br/><br/>

<!-- TODO: allow selecting roles/channels instead of using IDs -->

<div class="row row-cols-1 row-cols-md-3 g-4">
  {#each settings as setting, setting_index}
    <div class="col">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">
            <label for={`setting-${setting.key}`}>{setting.key.split("_").map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(" ")}</label>
          </h5>
          <hr class="mt-0" style="width: 1rem"/>

          {#if Array.isArray(setting.value)}
            {#each setting.value as value, i}
              <div class="row mt-2">
                <div class="col-10">
                  <input type="text" class="form-control" id={`array-${setting.key}-${i}`} placeholder={`${setting.key.split("_").map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(" ")} ID`} bind:value={settings[setting_index].value[i]}/>
                  <label for={`array-${setting.key}-${i}`} class="d-none">{setting.key.split("_").map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(" ")} {i}</label>
                </div>
                <div class="col-2">
                  <button type="button" class="btn btn-sm" style="margin-top: 0.2rem" on:click={removeArrayValue(setting_index, i)}>
                    {@html icons['x-circle'].toSvg({ color: "red", ...SVG_ATTRS })}
                  </button>
                </div>
              </div>
            {/each}

            <div class="row mt-3">
              <div class="col-6 text-center">
                <button type="button" class="btn btn-outline-success" on:click={update(setting_index)}>
                  {@html icons.save.toSvg(SVG_ATTRS)}
                  &nbsp; Save
                </button>
              </div>
              <div class="col-6 text-center">
                <button type="button" class="btn btn-outline-primary" on:click={addArrayValue(setting_index)}>
                  {@html icons['plus-circle'].toSvg(SVG_ATTRS)}
                  &nbsp;Add
                </button>
              </div>
            </div>
          {:else}
            <div class="row">
              <div class="col-9">
                <input type="text" class="form-control" id={`setting-${setting.key}`} placeholder={`${setting.key.split("_").map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(" ")} ID`} bind:value={settings[setting_index].value}/>
              </div>
              <div class="col-3">
                <button type="button" class="btn btn-outline-success" on:click={update(setting_index)}>
                  {@html icons.save.toSvg(SVG_ATTRS)}
                  &nbsp; Save
                </button>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>
  {/each}
</div>
