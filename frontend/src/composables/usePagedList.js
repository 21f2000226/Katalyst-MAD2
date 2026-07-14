import { computed, ref, watch } from "vue";

// client-side search and paging so tables for better UI and redability
export function usePagedList(sourceRef, options = {}) {
  const pageSize = options.pageSize || 8;
  const filterFn = options.filterFn || (() => true);
  const query = ref("");
  const page = ref(1);

  const filtered = computed(() => {
    const items = sourceRef.value || [];
    const q = query.value.trim().toLowerCase();
    if (!q) return items.filter((item) => filterFn(item, ""));
    return items.filter((item) => filterFn(item, q));
  });

  const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize)));

  const pageItems = computed(() => {
    const start = (page.value - 1) * pageSize;
    return filtered.value.slice(start, start + pageSize);
  });

  watch(query, () => {
    page.value = 1;
  });

  watch(sourceRef, () => {
    if (page.value > totalPages.value) page.value = totalPages.value;
  });

  function next() {
    if (page.value < totalPages.value) page.value += 1;
  }

  function prev() {
    if (page.value > 1) page.value -= 1;
  }

  function go(n) {
    page.value = Math.min(Math.max(1, n), totalPages.value);
  }

  return { query, page, pageSize, filtered, pageItems, totalPages, next, prev, go };
}
