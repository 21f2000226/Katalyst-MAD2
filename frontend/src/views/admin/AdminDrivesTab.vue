<script setup>
/**
 * Drives tab: all job positions with search, pager, and delete.
 */
import StatusBadge from "../../components/StatusBadge.vue";
import TablePager from "../../components/TablePager.vue";

defineProps({
  items: { type: Array, default: () => [] },
  query: { type: String, default: "" },
  page: { type: Number, required: true },
  totalPages: { type: Number, required: true },
  totalItems: { type: Number, required: true },
});

const emit = defineEmits(["update:query", "open", "act", "prev", "next", "go"]);

function act(method, path, okText) {
  emit("act", { method, path, okText });
}
</script>

<template>
  <div class="k-section-card">
    <div class="k-toolbar">
      <input
        :value="query"
        class="form-control form-control-sm"
        placeholder="Search drive, company, status..."
        @input="emit('update:query', $event.target.value)"
      />
    </div>
    <div class="table-responsive">
      <table class="table table-hover table-sm k-table mb-0">
        <thead>
          <tr>
            <th>Drive title</th>
            <th>Company</th>
            <th>Status</th>
            <th>Approval</th>
            <th class="text-end">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!items.length">
            <td colspan="5" class="text-muted text-center py-4">No drives match your search.</td>
          </tr>
          <tr v-for="j in items" :key="j.id" class="k-click-row" @click="emit('open', j.id)">
            <td>{{ j.title }}</td>
            <td>{{ j.company?.name }}</td>
            <td><StatusBadge :status="j.status" /></td>
            <td><StatusBadge :status="j.approval_status" /></td>
            <td class="text-end" @click.stop>
              <button
                class="btn btn-sm btn-danger"
                @click="act('DELETE', `/api/admin/job-positions/${j.id}`, 'Deleted')"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <TablePager
      :page="page"
      :total-pages="totalPages"
      :total-items="totalItems"
      @prev="emit('prev')"
      @next="emit('next')"
      @go="emit('go', $event)"
    />
  </div>
</template>
