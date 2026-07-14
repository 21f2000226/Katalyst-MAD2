<script setup>
/**
 * Shortlist modal for inviting applicants to a interview optional interview time/notes
 */
defineProps({
  open: { type: Boolean, default: false },
  interviewAt: { type: String, default: "" },
  interviewNotes: { type: String, default: "" },
});

const emit = defineEmits(["close", "confirm", "update:interviewAt", "update:interviewNotes"]);
</script>

<template>
  <div v-if="open" class="modal d-block" tabindex="-1" style="background: rgba(0, 0, 0, 0.5)">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Shortlist and schedule interview</h5>
          <button type="button" class="btn-close" aria-label="Close" @click="emit('close')" />
        </div>
        <div class="modal-body">

          <p class="small text-muted">
            Interview time is optional but recommended. The student gets an email in MailHog.
          </p>

          <label class="form-label">Interview date and time</label>


          <input
            :value="interviewAt"
            type="datetime-local"
            class="form-control mb-2"
            @input="emit('update:interviewAt', $event.target.value)"
          />

          <label class="form-label">Notes (location / link)</label>
          <input
            :value="interviewNotes"
            type="text"
            class="form-control"
            placeholder="e.g. Zoom link or campus room"
            @input="emit('update:interviewNotes', $event.target.value)"
          />

        </div>
        <div class="modal-footer">

          <button class="btn btn-secondary" @click="emit('close')">Cancel</button>
          <button class="btn btn-info" @click="emit('confirm')">Shortlist</button>
          
        </div>
      </div>
    </div>
  </div>
</template>
