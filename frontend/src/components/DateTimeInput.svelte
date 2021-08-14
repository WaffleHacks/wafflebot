<script>
  import Flatpickr from "svelte-flatpickr";
  import "flatpickr/dist/flatpickr.css";

  export let value, label;

  const options = {
    enableTime: true,
    dateFormat: "Z",

    altInput: true,
    altFormat: "Y-m-d h:i K",
  };

  const id = Math.floor(Math.random() * 1000);
</script>

<div class="form-floating">
  <Flatpickr id={`input-time-${id}`} {options} name="datetime" bind:value class="bg-white" />
  <label for={`input-time-${id}`}>{label}</label>
</div>
