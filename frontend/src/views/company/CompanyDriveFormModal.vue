<script setup>
/**
 * Create/edit placement drive modal for the company dashboard. */
defineProps({
  open: { type: Boolean, default: false },
  isEditing: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  driveForm: { type: Object, required: true },
});

defineEmits(["close", "save"]);
</script>

<template>
  <div
    v-if="open"
    class="modal d-block"
    tabindex="-1"
    style="background: rgba(35, 36, 40, 0.55)"
    @click.self="$emit('close')"
  >
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ isEditing ? "Edit placement drive" : "Post a new placement drive" }}</h5>
          <button type="button" class="btn-close" aria-label="Close" @click="$emit('close')" />
        </div>
        <div class="modal-body">
          <div v-if="isEditing" class="alert alert-warning py-2 small">
            Saving changes to an approved drive will set it back to pending until an admin accepts it again.
          </div>
          <div class="row g-3">
            <div class="col-md-8">
              <label class="form-label">Drive title</label>
              <input
                v-model="driveForm.title"
                class="form-control"
                placeholder="e.g. Software Engineer Campus Drive 2026"
              />
            </div>
            <div class="col-md-4">
              <label class="form-label">Application deadline</label>
              <input v-model="driveForm.deadline" type="date" class="form-control" />
            </div>
            <div class="col-12">
              <label class="form-label">Drive description</label>
              <textarea
                v-model="driveForm.description"
                class="form-control"
                rows="3"
                placeholder="Role overview, process rounds, location, and other details students should know"
              />
            </div>

            <div class="col-md-4">

              <label class="form-label">Minimum CGPA cutoff</label>
              
              <input
                v-model="driveForm.min_cgpa"
                type="number"
                step="0.01"
                min="0"
                max="10"
                class="form-control"
                placeholder="e.g. 7.5 (blank = no cutoff)"
              />

            </div>
            
            <div class="col-md-8">
              <label class="form-label">Other eligibility notes</label>
              <textarea
                v-model="driveForm.requirements"
                class="form-control"
                rows="2"
                placeholder="Branches, batch year, skills, and any other eligibility rules"
              />
            </div>
            
            <div class="col-md-6">
             <label class="form-label">Minimum package (LPA)</label>
              <input
                v-model="driveForm.salary_min"
                type="number"
                step="0.1"
                min="0"
                class="form-control"
                placeholder="e.g. 6"
              />
            </div>
            
            <div class="col-md-6">
              <label class="form-label">Maximum package (LPA)</label>
              <input
                v-model="driveForm.salary_max"
                type="number"
                step="0.1"
                min="0"
                class="form-control"
                placeholder="e.g. 12"
              />
            
            </div>
          </div>
        </div>
        <div class="modal-footer">

          <button type="button" class="btn btn-outline-secondary" @click="$emit('close')">Cancel</button>
          <button type="button" class="btn btn-primary" :disabled="saving" @click="$emit('save')">
            {{ saving ? "Saving..." : isEditing ? "Save changes" : "Submit for approval" }}
          </button>
          
        </div>
      </div>
    </div>
  </div>
</template>
