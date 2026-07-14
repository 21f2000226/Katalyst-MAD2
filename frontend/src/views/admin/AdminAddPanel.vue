<script setup>
/**
 * Add-records flow: pick student/company/drive, then fill the modal form.
 * Parent owns the reactive form objects and save handlers.
 */
defineProps({
  showModal: { type: Boolean, default: false },
  addKind: { type: String, default: null },
  newStudent: { type: Object, required: true },
  newCompany: { type: Object, required: true },
  newJob: { type: Object, required: true },
});

const emit = defineEmits(["choose", "close", "save-student", "save-company", "save-job"]);
</script>

<template>
  <div>
    <!-- Stage 1: choose what to add -->
    <div class="row g-3">
      <div class="col-md-4">
        <button type="button" class="k-section-card k-add-pick w-100 text-start" @click="emit('choose', 'student')">
          <h5 class="mb-1">Add student</h5>
          <p class="small text-muted mb-0">Create a student account and profile.</p>
        </button>
      </div>
      <div class="col-md-4">
        <button type="button" class="k-section-card k-add-pick w-100 text-start" @click="emit('choose', 'company')">
          <h5 class="mb-1">Add company</h5>
          <p class="small text-muted mb-0">Create a company account (auto-approved).</p>
        </button>
      </div>
      <div class="col-md-4">
        <button type="button" class="k-section-card k-add-pick w-100 text-start" @click="emit('choose', 'drive')">
          <h5 class="mb-1">Add drive</h5>
          <p class="small text-muted mb-0">Create a placement drive for a company.</p>
        </button>
      </div>
    </div>

    <!-- Stage 2: add form modal (teleported visually via parent layout) -->
    <div
      v-if="showModal"
      class="modal d-block"
      style="background: rgba(35, 36, 40, 0.55)"
      @click.self="emit('close')"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <template v-if="addKind === 'student'">Add student</template>
              <template v-else-if="addKind === 'company'">Add company</template>
              <template v-else>Add drive</template>
            </h5>
            <button type="button" class="btn-close" aria-label="Close" @click="emit('close')" />
          </div>
          <div class="modal-body">
            <div v-if="addKind === 'student'" class="vstack gap-2">
              <label class="form-label mb-0">Username</label>
              <input v-model="newStudent.username" class="form-control" />
              <label class="form-label mb-0">Email</label>
              <input v-model="newStudent.email" class="form-control" />
              <label class="form-label mb-0">Password</label>
              <input v-model="newStudent.password" type="password" class="form-control" />
              <label class="form-label mb-0">Full name</label>
              <input v-model="newStudent.full_name" class="form-control" />
              <label class="form-label mb-0">CGPA</label>
              <input v-model="newStudent.cgpa" class="form-control" />
              <label class="form-label mb-0">Graduation year</label>
              <input v-model="newStudent.graduation_year" class="form-control" />
            </div>
            <div v-else-if="addKind === 'company'" class="vstack gap-2">
              <label class="form-label mb-0">Username</label>
              <input v-model="newCompany.username" class="form-control" />
              <label class="form-label mb-0">Email</label>
              <input v-model="newCompany.email" class="form-control" />
              <label class="form-label mb-0">Password</label>
              <input v-model="newCompany.password" type="password" class="form-control" />
              <label class="form-label mb-0">Company name</label>
              <input v-model="newCompany.company_name" class="form-control" />
              <label class="form-label mb-0">Industry</label>
              <input v-model="newCompany.industry" class="form-control" />
            </div>
            <div v-else class="vstack gap-2">
              <label class="form-label mb-0">Company ID</label>
              <input v-model="newJob.company_id" class="form-control" placeholder="Existing company id" />
              <label class="form-label mb-0">Drive title</label>
              <input v-model="newJob.title" class="form-control" />
              <label class="form-label mb-0">Description</label>
              <textarea v-model="newJob.description" class="form-control" rows="3" />
              <label class="form-label mb-0">Minimum CGPA cutoff</label>
              <input
                v-model="newJob.min_cgpa"
                type="number"
                step="0.01"
                min="0"
                max="10"
                class="form-control"
                placeholder="Blank = no cutoff"
              />
              <label class="form-label mb-0">Other eligibility notes</label>
              <textarea v-model="newJob.requirements" class="form-control" rows="2" />
              <label class="form-label mb-0">Deadline</label>
              <input v-model="newJob.deadline" type="date" class="form-control" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" @click="emit('close')">Cancel</button>
            <button
              v-if="addKind === 'student'"
              type="button"
              class="btn btn-primary"
              @click="emit('save-student')"
            >
              Save student
            </button>
            <button
              v-else-if="addKind === 'company'"
              type="button"
              class="btn btn-primary"
              @click="emit('save-company')"
            >
              Save company
            </button>
            <button v-else type="button" class="btn btn-primary" @click="emit('save-job')">Save drive</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
