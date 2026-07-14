<script setup>
/**
 * Stat cards row at the top of the admin dashboard.
 */
defineProps({
  stats: { type: Object, default: () => ({}) },
});
</script>

<template>
  <div class="row g-3 mb-4">
    <div v-for="(val, key) in stats" :key="key" class="col-6 col-md-4 col-xl-2">
      <div class="card k-stat-card text-center h-100">
        <div class="card-body py-3">
          <div class="k-stat-value">{{ val }}</div>
          <div class="k-stat-label">{{ key.replace(/_/g, " ") }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
