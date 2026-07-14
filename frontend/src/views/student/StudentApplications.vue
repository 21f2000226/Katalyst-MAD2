<script setup>
import { computed, onMounted, ref } from "vue";
import { api, openAuthedFile } from "../../api/client";
import StatusBadge from "../../components/StatusBadge.vue";
import TablePager from "../../components/TablePager.vue";
import { usePagedList } from "../../composables/usePagedList";
import { pushToast } from "../../services/toast";

const data = ref(null);
const loading = ref(true);
const exportBusy = ref(false);

const appsSrc = computed(() => data.value?.applications || []);
// student applications and exports in csv and emauil
const {
  query: appQuery,
  page: appPage,
  pageItems: appItems,
  filtered: appFiltered,
  totalPages: appPages,
  prev: appPrev,
  next: appNext,
  go: appGo,
} = usePagedList(appsSrc, {
  pageSize: 8,
  filterFn: (app, q) => {
    if (!q) return true;
    const hay = `${app.job_position?.title || ""} ${app.job_position?.company?.name || ""} ${app.status || ""}`.toLowerCase();
    return hay.includes(q);
  },
});

function showMsg(text, type = "success") {
  pushToast(text, type);
}

async function load() {
  loading.value = true;
  try {
    data.value = await api("/api/student/dashboard");
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    loading.value = false;
  }
}

async function withdraw(appId) {
  try {
    await api(`/api/student/applications/${appId}`, { method: "DELETE" });
    showMsg("Application withdrawn");
    await load();
  } catch (e) {
    showMsg(e.message, "danger");
  }
}

// export via download | email | both
async function exportApplications(delivery) {
  exportBusy.value = true;
  try {
    const started = await api("/api/jobs/exports/applications", {
      method: "POST",
      body: JSON.stringify({ delivery }),
    });
    const taskId = started.task_id;

    if (delivery === "email") {
      showMsg("Export queued. You will get an email in MailHog when it is ready.", "info");
      exportBusy.value = false;
      return;
    }

    showMsg("Export queued. Preparing CSV...", "info");

    for (let i = 0; i < 20; i++) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const status = await api(`/api/jobs/tasks/${taskId}`);
      if (status.state === "SUCCESS" && status.result?.ok) {
        await openAuthedFile(`/api/jobs/exports/${status.result.filename}`);
        const mailNote = status.result.emailed ? " Also emailed to MailHog." : "";
        showMsg(`Export ready (${status.result.row_count} rows).${mailNote}`);
        return;
      }

      if (status.state === "FAILURE" || (status.state === "SUCCESS" && !status.result?.ok)) {
        throw new Error(status.error || status.result?.error || "Export failed");
      }
    }

    throw new Error("Export is taking too long. Check Celery worker is running.");
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    exportBusy.value = false;
  }
}

onMounted(load);

</script>

<template>
  <div>
    <div v-if="loading" class="text-muted py-5 text-center">Loading applications...</div>
    <div v-else class="k-bento">
      <div class="k-bento-tile k-bento-tile--toolbar k-bento-span-12">
        <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
          <h2 class="k-bento-tile__title mb-0">My applications</h2>
          <div class="d-flex flex-wrap gap-2 align-items-center">

            <input
              v-model="appQuery"
              class="form-control form-control-sm"
              style="max-width: 220px"
              placeholder="Search..."
            />
            <div class="dropdown">

              <button
                class="btn btn-sm btn-outline-primary dropdown-toggle"
                type="button"
                data-bs-toggle="dropdown"
                data-bs-popper-config='{"strategy":"fixed"}'
                aria-expanded="false"
                :disabled="exportBusy"
              >
                {{ exportBusy ? "Working..." : "Export" }}
              </button>
              <ul class="dropdown-menu dropdown-menu-end">
                <li>
                  <button type="button" class="dropdown-item" @click="exportApplications('download')">
                    Download
                  </button>
                </li>
                <li>
                  <button type="button" class="dropdown-item" @click="exportApplications('email')">
                    Email
                  </button>
                </li>
              </ul>

            </div>

          </div>
        </div>

        <div class="table-responsive">
          <table class="table table-hover table-sm k-table mb-0">

            <thead>
                <tr>
                  <th>Drive</th>
                  <th>Company</th>
                  <th>Status</th>
                  <th>Interview</th>
                  <th class="text-end">Actions</th>
                </tr>

            </thead>
            <tbody>

              <tr v-if="!appItems.length">
                <td colspan="5" class="text-muted text-center py-4">No applications yet.</td>
              </tr>
              <tr v-for="app in appItems" :key="app.id">
                <td>{{ app.job_position?.title }}</td>
                <td>{{ app.job_position?.company?.name }}</td>
                <td><StatusBadge :status="app.status" /></td>
                <td class="small text-muted">
                  {{ app.interview_at ? app.interview_at.replace("T", " ").slice(0, 16) : "-" }}
                </td>
                <td class="text-end">
                  <button
                    v-if="app.status === 'applied'"
                    class="btn btn-sm btn-outline-danger"
                    @click="withdraw(app.id)"
                  >
                    Withdraw

                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <TablePager
          :page="appPage"
          :total-pages="appPages"
          :total-items="appFiltered.length"
          @prev="appPrev"
          @next="appNext"
          @go="appGo"
        />
        
      </div>
    </div>
  </div>
</template>
