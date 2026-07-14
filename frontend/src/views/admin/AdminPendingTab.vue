<script setup>
/**
 * Pending tab: companies and drives waiting for admin approve/reject.
 * Parent owns API calls via the act event.
 */
defineProps({
  pendingCompanies: { type: Array, default: () => [] },
  pendingJobs: { type: Array, default: () => [] },
});

const emit = defineEmits(["open-company", "open-drive", "act"]);

function act(method, path, okText) {
  emit("act", { method, path, okText });
}
</script>

<template>
  <div class="row g-3">
    <div class="col-lg-6">
      <div class="k-section-card">
        <h5>Pending companies ({{ pendingCompanies.length }})</h5>
        <div v-if="!pendingCompanies.length" class="k-empty py-4">
          <div class="k-empty__title">No pending companies</div>
        </div>
        <div
          v-for="c in pendingCompanies"
          :key="c.id"
          class="card k-card mb-2 k-click-row"
          @click="emit('open-company', c.id)"
        >
          <div class="card-body d-flex flex-wrap justify-content-between align-items-center gap-2">
            <div>
              <strong>{{ c.name }}</strong>
              <div class="small text-muted">{{ c.industry || "No industry" }}</div>
            </div>
            <div class="btn-group btn-group-sm" @click.stop>
              <button
                class="btn btn-success"
                @click="act('POST', `/api/admin/companies/${c.id}/approve`, 'Approved')"
              >
                Approve
              </button>
              <button
                class="btn btn-warning"
                @click="act('POST', `/api/admin/companies/${c.id}/reject`, 'Rejected')"
              >
                Reject
              </button>
              <button
                class="btn btn-danger"
                @click="act('POST', `/api/admin/companies/${c.id}/blacklist`, 'Blacklisted')"
              >
                Blacklist
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="col-lg-6">
      <div class="k-section-card">
        <h5>Pending drives ({{ pendingJobs.length }})</h5>
        <div v-if="!pendingJobs.length" class="k-empty py-4">
          <div class="k-empty__title">No pending drives</div>
        </div>
        <div
          v-for="j in pendingJobs"
          :key="j.id"
          class="card k-card mb-2 k-click-row"
          @click="emit('open-drive', j.id)"
        >
          <div class="card-body d-flex flex-wrap justify-content-between align-items-center gap-2">
            <div>
              <strong>{{ j.title }}</strong>
              <div class="small text-muted">{{ j.company?.name }}</div>
            </div>
            <div class="btn-group btn-group-sm" @click.stop>
              <button
                class="btn btn-success"
                @click="act('POST', `/api/admin/job-positions/${j.id}/approve`, 'Approved')"
              >
                Approve
              </button>
              <button
                class="btn btn-warning"
                @click="act('POST', `/api/admin/job-positions/${j.id}/reject`, 'Rejected')"
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
