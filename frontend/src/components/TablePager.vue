<script setup>
import { computed } from "vue";
//easily build tables
const props = defineProps({
  page: { type: Number, required: true },
  totalPages: { type: Number, required: true },
  totalItems: { type: Number, default: 0 },
});

const emit = defineEmits(["prev", "next", "go"]);

const visiblePages = computed(() => {
  const total = props.totalPages;
  const current = props.page;
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  const pages = new Set([1, total, current, current - 1, current + 1]);
  return [...pages].filter((n) => n >= 1 && n <= total).sort((a, b) => a - b);
});
</script>

<template>
  <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mt-3">
    <span class="text-muted small">
      {{ totalItems }} result{{ totalItems === 1 ? "" : "s" }}
      <span v-if="totalPages > 1"> · page {{ page }} of {{ totalPages }}</span>
    </span>
    <div v-if="totalPages > 1" class="btn-group btn-group-sm">
      <button type="button" class="btn btn-outline-secondary" :disabled="page <= 1" @click="emit('prev')">
        Prev
      </button>
      <template v-for="(n, idx) in visiblePages" :key="n">
        <span
          v-if="idx > 0 && n - visiblePages[idx - 1] > 1"
          class="btn btn-outline-secondary disabled"
        >…</span>
        <button
          type="button"
          class="btn"
          :class="n === page ? 'btn-primary' : 'btn-outline-secondary'"
          @click="emit('go', n)"
        >

          {{ n }}
        </button>
      </template>
      <button
        type="button"
        class="btn btn-outline-secondary"
        :disabled="page >= totalPages"
        @click="emit('next')"
      >

        Next
      </button>
    </div>
  </div>
</template>
