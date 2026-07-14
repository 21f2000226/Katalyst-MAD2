<script setup>
/**
 * Admin dashboard nav bar b/w for switching between studenst, companies, pending approvals and adding
 */
defineProps({
  activeTab: { type: String, required: true },
  pendingCount: { type: Number, default: 0 },
});

defineEmits(["open-tab"]);
</script>

<template>
  <ul class="nav nav-tabs mb-3">
    <li class="nav-item">
      <button
        class="nav-link"
        :class="{ active: activeTab === 'pending' }"
        type="button"
        @click="$emit('open-tab', 'pending')"
      >
        Pending
        <span v-if="pendingCount" class="badge bg-warning text-dark ms-1">{{ pendingCount }}</span>
      </button>
    </li>
    <li class="nav-item">
      <button
        class="nav-link"
        :class="{ active: activeTab === 'students' }"
        type="button"
        @click="$emit('open-tab', 'students')"
      >
        Students
      </button>
    </li>
    <li class="nav-item">
      <button
        class="nav-link"
        :class="{ active: activeTab === 'companies' }"
        type="button"
        @click="$emit('open-tab', 'companies')"
      >
        Companies
      </button>
    </li>
    <li class="nav-item">
      <button
        class="nav-link"
        :class="{ active: activeTab === 'jobs' }"
        type="button"
        @click="$emit('open-tab', 'jobs')"
      >
        Drives
      </button>
    </li>
    <li class="nav-item">
      <button
        class="nav-link"
        :class="{ active: activeTab === 'placements' }"
        type="button"
        @click="$emit('open-tab', 'placements')"
      >
        Placements
      </button>
    </li>
    <li class="nav-item">
      <button
        class="nav-link"
        :class="{ active: activeTab === 'add' }"
        type="button"
        @click="$emit('open-tab', 'add')"
      >
        Add records
      </button>
    </li>
  </ul>
</template>
