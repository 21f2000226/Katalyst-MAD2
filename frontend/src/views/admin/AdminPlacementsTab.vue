<script setup>
/**
 * Placements tab - confirmed placementst.
 */
defineProps({
  placements: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
});

defineEmits(["refresh"]);
</script>

<template>

  <div class="k-section-card">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h5 class="mb-0">Confirmed placements</h5>
      <button class="btn btn-sm btn-outline-secondary" :disabled="loading" @click="$emit('refresh')">
        {{ loading ? "Loading..." : "Refresh" }}
      </button>
    </div>
    <div class="table-responsive">
      <table class="table table-hover table-sm k-table mb-0">
        <thead>
          <tr>
            <th>Student</th>
            <th>Company</th>
            <th>Drive</th>
            <th>Salary (LPA)</th>
            <th>Joining</th>
            <th>Placed at</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6" class="text-muted text-center py-4">Loading placements...</td>
          </tr>
          <tr v-else-if="!placements.length">
            <td colspan="6" class="text-muted text-center py-4">No placements recorded yet.</td>
          </tr>
          <tr v-for="p in placements" :key="p.id">
            <td>{{ p.student_name || "-" }}</td>
            <td>{{ p.company_name || "-" }}</td>
            <td>{{ p.job_title || "-" }}</td>
            <td>{{ p.salary }}</td>
            <td>{{ p.joining_date || "-" }}</td>
            <td class="small text-muted">
              {{ p.placed_at ? p.placed_at.replace("T", " ").slice(0, 16) : "-" }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  
</template>
