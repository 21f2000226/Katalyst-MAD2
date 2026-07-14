<script setup>
/**
 * Students tab-  searchable paged table with blacklist/unblacklist students.
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
        placeholder="Search name, email, username..."
        @input="emit('update:query', $event.target.value)"
      />
    </div>
    <div class="table-responsive">
      <table class="table table-hover table-sm k-table mb-0">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>CGPA</th>
            <th>Year</th>
            <th>Account</th>
            <th class="text-end">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!items.length">
            <td colspan="6" class="text-muted text-center py-4">No students match your search.</td>
          </tr>
          <tr v-for="s in items" :key="s.id" class="k-click-row" @click="emit('open', s.id)">
            <td>{{ s.full_name }}</td>
            <td>{{ s.user?.email }}</td>
            <td>{{ s.cgpa ?? "-" }}</td>
            <td>{{ s.graduation_year ?? "-" }}</td>
            <td>
              <StatusBadge v-if="s.user?.role === 'blacklisted'" status="blacklisted" />
              <span v-else class="badge bg-light text-dark border">Active</span>
            </td>
            <td class="text-end text-nowrap" @click.stop>
              <button
                v-if="s.user?.role === 'blacklisted'"
                class="btn btn-sm btn-success me-1"
                @click="act('POST', `/api/admin/students/${s.id}/unblacklist`, 'Student re-enabled')"
              >
                Re-enable
              </button>
              <button
                v-else
                class="btn btn-sm btn-outline-danger me-1"
                @click="act('POST', `/api/admin/students/${s.id}/blacklist`, 'Blacklisted')"
              >
                Blacklist
              </button>
              <button
                class="btn btn-sm btn-danger"
                @click="act('DELETE', `/api/admin/students/${s.id}`, 'Deleted')"
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
