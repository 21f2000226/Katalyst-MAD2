<script setup>
/**
 * placement selection modal on a applicant selection, update salary and date of joining
 */
defineProps({
  open: { type: Boolean, default: false },
  salary: { type: String, default: "" },
  joiningDate: { type: String, default: "" },
});

const emit = defineEmits(["close", "confirm", "update:salary", "update:joiningDate"]);
</script>

<template>
  <div v-if="open" class="modal d-block" tabindex="-1" style="background: rgba(0, 0, 0, 0.5)">
    <div class="modal-dialog">
      
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Confirm placement</h5>
          <button type="button" class="btn-close" aria-label="Close" @click="emit('close')" />
        </div>

        <div class="modal-body">
          <label class="form-label">Salary (LPA)</label>
          <input
            :value="salary"
            type="number"
            step="0.1"
            class="form-control mb-2"
            @input="emit('update:salary', $event.target.value)"
          />
          <label class="form-label">Joining date</label>
          <input
            :value="joiningDate"
            type="date"
            class="form-control"
            @input="emit('update:joiningDate', $event.target.value)"
          />
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="emit('close')">Cancel</button>
          <button class="btn btn-success" @click="emit('confirm')">Confirm</button>
        </div>

      </div>
    </div>
  </div>
</template>
