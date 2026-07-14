<script setup>

import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { api, openAuthedFile } from "../../api/client";
import ClosableTip from "../../components/ClosableTip.vue";
import TablePager from "../../components/TablePager.vue";
import StatusBadge from "../../components/StatusBadge.vue";
import { usePagedList } from "../../composables/usePagedList";
import { pushToast } from "../../services/toast";
import CompanyDriveFormModal from "./CompanyDriveFormModal.vue";

const router = useRouter();
const data = ref(null);
const loading = ref(true);
const exportBusy = ref(false);
const showForm = ref(false);
const editingId = ref(null);
const saving = ref(false);

/**
 * Company drives list to post/edit drives, export applications via download or email, close/reopen drives. reopening  needs admin approval again. */

 const driveForm = reactive({

  title: "",
  description: "",
  requirements: "",
  min_cgpa: "",
  salary_min: "",
  salary_max: "",
  deadline: "",
});

const AllDrives = computed(() => {
  if (!data.value) return [];
  return [
    ...(data.value.approved_job_positions || []),
    ...(data.value.pending_job_positions || []),
    ...(data.value.rejected_job_positions || []),
  ];
});

const pendingCount = computed(() => data.value?.pending_job_positions?.length || 0);
const approvedCount = computed(() => data.value?.approved_job_positions?.length || 0);
const isEditing = computed(() => editingId.value != null);

const {
  query: driveQuery,
  page: drivePage,
  pageItems: driveItems,
  filtered: driveFiltered,
  totalPages: drivePages,
  prev: drivePrev,
  next: driveNext,
  go: driveGo,
} = usePagedList(AllDrives, {
  pageSize: 6,
  filterFn: (drive, q) => {
    if (!q) return true;
    const hay = `${drive.title || ""} ${drive.status || ""} ${drive.approval_status || ""}`.toLowerCase();
    return hay.includes(q);
  },
});

function showMsg(text, type = "success") {
  pushToast(text, type);
}

function toDateInput(value) {
  if (!value) return "";
  return String(value).slice(0, 10);
}


function resetForm() {
  Object.assign(driveForm, {
    title: "",
    description: "",
    requirements: "",
    min_cgpa: "",
    salary_min: "",
    salary_max: "",
    deadline: "",
  });

  editingId.value = null;
}

function openCreate() {
  resetForm();
  showForm.value = true;

}

function openEdit(drive) {
  editingId.value = drive.id;

  Object.assign(driveForm, {
    title: drive.title || "",
    description: drive.description || "",
    requirements: drive.requirements || "",
    min_cgpa: drive.min_cgpa ?? "",
    salary_min: drive.salary_min ?? "",
    salary_max: drive.salary_max ?? "",
    deadline: toDateInput(drive.deadline),
  });

  showForm.value = true;
}

function closeForm() {
  showForm.value = false;

  resetForm();
}

function statusActionLabel(drive) {
  return drive.status === "active" ? "Close drive" : "Request reopen";

}

async function load() {
  loading.value = true;

  try {
    data.value = await api("/api/company/dashboard");
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    loading.value = false;
  }

}

async function saveDrive() {
  saving.value = true;
  
  try {
    if (isEditing.value) {
      const res = await api(`/api/company/job-positions/${editingId.value}`, {
        method: "PUT",
        body: JSON.stringify(driveForm),
      });
      showMsg(res.message || "Drive updated");
    } 
  else {
      await api("/api/company/job-positions", {
        method: "POST",
        body: JSON.stringify(driveForm),
      });
      showMsg("Drive submitted for admin approval");
    }
    closeForm();
    await load();
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    saving.value = false;
  }

}

async function setDriveOpenState(drive) {

  const closing = drive.status === "active";

  const confirmMsg = closing
    ? "Close this drive? Students will no longer be able to apply."
    : "Request reopen? An admin must approve this drive again before it goes live.";

  if (!confirm(confirmMsg)) return;

  try {
    const res = await api(`/api/company/job-positions/${drive.id}/toggle`, { method: "POST" });
    showMsg(res.message || (closing ? "Drive closed" : "Reopen requested"));
    await load();
  } catch (e) {
    showMsg(e.message, "danger");
  }

}

async function deleteDrive(id) {
  /**Deleting a drive */
  if (!confirm("Delete this drive?")) return;
  try {
    await api(`/api/company/job-positions/${id}`, { method: "DELETE" });
    showMsg("Drive deleted");
    await load();
  } catch (e) {
    showMsg(e.message, "danger");
  }
}

async function exportApplications(delivery) {
  exportBusy.value = true;
  try {
    const started = await api("/api/jobs/exports/applications", {
      method: "POST",
      body: JSON.stringify({ delivery }),
    });
    const taskId = started.task_id;

    if (delivery === "email") {
      showMsg("Export queued. CSV will appear in MailHog when ready.", "info");
      exportBusy.value = false;
      return;
    }

    showMsg("Export queued...", "info");
    for (let i = 0; i < 20; i++) {
      await new Promise((r) => setTimeout(r, 1000));
      const status = await api(`/api/jobs/tasks/${taskId}`);
      if (status.state === "SUCCESS" && status.result?.ok) {
        await openAuthedFile(`/api/jobs/exports/${status.result.filename}`);
        showMsg(`Export ready (${status.result.row_count} rows).`);
        return;
      }

      if (status.state === "FAILURE" || (status.state === "SUCCESS" && !status.result?.ok)) {
        throw new Error(status.error || status.result?.error || "Export failed");
      }

    }

    throw new Error("Export timed out. Is the Celery worker running?");
    
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
    <div v-if="loading" class="text-muted py-5 text-center">Loading drives...</div>
    <div v-else-if="data" class="k-bento">
      <div class="k-bento-tile k-bento-tile--ink k-bento-span-5">
        <div class="k-bento-tile__label">Company</div>
        <h1 class="k-page-title text-white mb-2">{{ data.company.name }}</h1>
        <StatusBadge :status="data.company.approval_status" />
        <p class="k-page-subtitle mt-2 mb-0">Post placement drives, review applicants, and view resumes.</p>
      </div>

      <div class="k-bento-span-7 k-bento-stats" style="grid-template-columns: repeat(3, minmax(0, 1fr))">
        <div class="k-bento-tile k-bento-tile--sky">
          <div class="k-bento-tile__label">Drives</div>
          <div class="k-bento-tile__value">{{ AllDrives.length }}</div>
          <div class="small mt-1 text-muted">{{ approvedCount }} approved · {{ pendingCount }} pending</div>
        </div>
        <div class="k-bento-tile k-bento-tile--sea">
          <div class="k-bento-tile__label">Applications</div>
          <div class="k-bento-tile__value">{{ data.stats.total_applications }}</div>
        </div>
        <div class="k-bento-tile">
          <div class="k-bento-tile__label">Pipeline</div>
          <div class="d-flex gap-3 mt-1">
            <div>
              <div class="k-bento-tile__value" style="font-size: 1.4rem">{{ data.stats.total_shortlisted }}</div>
              <div class="small text-muted">Shortlisted</div>
            </div>
            <div>
              <div class="k-bento-tile__value" style="font-size: 1.4rem">{{ data.stats.total_selected }}</div>
              <div class="small text-muted">Selected</div>
            </div>
          </div>
        </div>
      </div>

      <div class="k-bento-tile k-bento-tile--toolbar k-bento-span-12 py-2">
        <div class="d-flex flex-wrap gap-2">
          <button class="btn btn-sm btn-primary" @click="openCreate">Post new drive</button>
          <div class="dropdown">
            <button
              class="btn btn-sm btn-outline-primary dropdown-toggle"
              type="button"
              data-bs-toggle="dropdown"
              data-bs-popper-config='{"strategy":"fixed"}'
              aria-expanded="false"
              :disabled="exportBusy"
            >
              {{ exportBusy ? "Exporting..." : "Export" }}
            </button>
            <ul class="dropdown-menu">
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

      <div class="k-bento-tile k-bento-span-8">
        <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
          <h2 class="k-bento-tile__title mb-0">Your drives</h2>
          <input
            v-model="driveQuery"
            class="form-control form-control-sm"
            style="max-width: 220px"
            placeholder="Search drives..."
          />
        </div>
        <div class="table-responsive">
          <table class="table table-hover table-sm k-table mb-0">
            <thead>
              <tr>
                <th>Drive title</th>
                <th>Deadline</th>
                <th>Status</th>
                <th>Approval</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!driveItems.length">
                <td colspan="5" class="text-muted text-center py-4">No drives yet. Post one to get started.</td>
              </tr>
              <tr v-for="drive in driveItems" :key="drive.id">
                <td class="fw-medium">{{ drive.title }}</td>
                <td>{{ drive.deadline || "-" }}</td>
                <td><StatusBadge :status="drive.status" /></td>
                <td><StatusBadge :status="drive.approval_status" /></td>
                <td class="text-end text-nowrap">
                  <button
                    class="btn btn-sm btn-outline-primary me-1"
                    @click="router.push(`/company/drives/${drive.id}`)"
                  >
                    Applicants
                  </button>
                  <button class="btn btn-sm btn-outline-secondary me-1" @click="openEdit(drive)">Edit</button>
                  <button class="btn btn-sm btn-outline-warning me-1" @click="setDriveOpenState(drive)">
                    {{ statusActionLabel(drive) }}
                  </button>
                  <button class="btn btn-sm btn-outline-danger" @click="deleteDrive(drive.id)">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <TablePager
          :page="drivePage"
          :total-pages="drivePages"
          :total-items="driveFiltered.length"
          @prev="drivePrev"
          @next="driveNext"
          @go="driveGo"
        />
      </div>

      <ClosableTip class="k-bento-span-4" title="Hiring notes" storage-key="tip-company-drives">
        <p class="small mb-2">
          <strong>Close drive</strong> stops applications immediately.
          <strong>Request reopen</strong> sends a closed drive back for admin approval.
        </p>
        <p class="small mb-0">
          Editing an already approved drive also requires admin approval again.
        </p>
      </ClosableTip>
    </div>

    <CompanyDriveFormModal
      :open="showForm"
      :is-editing="isEditing"
      :saving="saving"
      :drive-form="driveForm"
      @close="closeForm"
      @save="saveDrive"
    />
  </div>
</template>
