<script setup>
/**
 * Show applicants details, and status. On clicking on a row it expands into full detailed student vue ( see what I did there ! lol)
 */
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api, fetchAuthedBlob, openAuthedFile } from "../../api/client";
import StatusBadge from "../../components/StatusBadge.vue";
import TablePager from "../../components/TablePager.vue";
import { usePagedList } from "../../composables/usePagedList";
import { pushToast } from "../../services/toast";
import CompanyApplicantModal from "./CompanyApplicantModal.vue";
import CompanySelectModal from "./CompanySelectModal.vue";
import CompanyShortlistModal from "./CompanyShortlistModal.vue";

const route = useRoute();
const router = useRouter();
const job = ref(null);
const applications = ref([]);
const loading = ref(true);
const selectModal = ref({ open: false, appId: null, salary: "", joining_date: "" });
const shortlistModal = ref({ open: false, appId: null, interview_at: "", interview_notes: "" });
const statusFilter = ref("all");

const selectedApp = ref(null);
const resumeUrl = ref("");
const resumeIsPdf = ref(false);
const resumeLoading = ref(false);
const resumeError = ref("");

const appsSrc = computed(() => {
  const list = applications.value || [];
  if (statusFilter.value === "all") return list;
  return list.filter((a) => a.status === statusFilter.value);
});

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
    const hay = `${app.student?.full_name || ""} ${app.student?.user?.email || ""} ${app.status || ""}`.toLowerCase();
    return hay.includes(q);
  },
});

function showMsg(text, type = "success") {
  pushToast(text, type);
}

function revokeResumeUrl() {
  if (resumeUrl.value) {
    URL.revokeObjectURL(resumeUrl.value);
    resumeUrl.value = "";
  }

  resumeIsPdf.value = false;
  resumeError.value = "";
}

async function loadResume(studentId, resumePath) {

  revokeResumeUrl();
  if (!resumePath) return;
  resumeLoading.value = true;
  try {
    const path = `/api/company/students/${studentId}/resume`;
    const file = await fetchAuthedBlob(path);
    const lower = (resumePath || "").toLowerCase();
    resumeIsPdf.value = file.isPdf || lower.endsWith(".pdf");
    resumeUrl.value = file.url;
  } catch (e) {
    resumeError.value = e.message || "Could not load resume.";
  } finally {
    resumeLoading.value = false;
  }
}

async function openApplicant(app) {
  selectedApp.value = app;
  await loadResume(app.student_id, app.student?.resume_path);
}

function closeApplicant() {
  selectedApp.value = null;
  revokeResumeUrl();
}

async function load() {
  loading.value = true;
  try {
    const data = await api(`/api/company/job-positions/${route.params.id}`);
    job.value = data.job_position;
    applications.value = data.applications || [];
    // refresh selected applicant after shortlist/select
    if (selectedApp.value) {
      const refreshed = applications.value.find((a) => a.id === selectedApp.value.id);
      if (refreshed) selectedApp.value = refreshed;
      else closeApplicant();
    }
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    loading.value = false;
  }
}

async function setStatus(appId, status, extra = {}) {
  try {
    const res = await api(`/api/company/applications/${appId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status, ...extra }),
    });
    if (status === "shortlisted" && res.emailed) {
      showMsg("Shortlisted. Interview reminder emailed to student (MailHog).");
    } else {
      showMsg("Status updated");
    }
    selectModal.value.open = false;
    shortlistModal.value.open = false;
    await load();
  } catch (e) {
    showMsg(e.message, "danger");
  }
}

function openShortlist(appId) {
  shortlistModal.value = { open: true, appId, interview_at: "", interview_notes: "" };
}

function confirmShortlist() {
  setStatus(shortlistModal.value.appId, "shortlisted", {
    interview_at: shortlistModal.value.interview_at || null,
    interview_notes: shortlistModal.value.interview_notes || null,
  });
}

function openSelect(appId) {
  selectModal.value = { open: true, appId, salary: "", joining_date: "" };
}

function confirmSelect() {
  if (!selectModal.value.salary) {
    showMsg("Enter salary (LPA) to confirm placement.", "warning");
    return;
  }
  setStatus(selectModal.value.appId, "selected", {
    salary: selectModal.value.salary,
    joining_date: selectModal.value.joining_date || undefined,
  });
}

async function openResumeExternal() {
  if (!selectedApp.value?.student?.resume_path) return;
  try {
    await openAuthedFile(`/api/company/students/${selectedApp.value.student_id}/resume`);
  } catch (e) {
    showMsg(e.message || "Could not open resume.", "danger");
  }
}

watch(statusFilter, () => {
  appPage.value = 1;
});

onMounted(load);

onBeforeUnmount(() => {
  revokeResumeUrl();
});
</script>

<template>
  <div>
    <div v-if="loading" class="text-muted py-5 text-center">Loading applicants...</div>
    <div v-else-if="job" class="k-bento">
      <div class="k-bento-tile k-bento-tile--ink k-bento-span-8">
        <button class="btn btn-sm btn-outline-light mb-2" @click="router.push('/company/drives')">
          Back to my drives
        </button>
        <h1 class="k-page-title text-white mb-1">{{ job.title }}</h1>
        <p class="k-page-subtitle mb-0">
          {{ applications.length }} applicant{{ applications.length === 1 ? "" : "s" }}
          · click a student to review their profile and resume
        </p>
      </div>
      <div class="k-bento-tile k-bento-tile--sky k-bento-span-4">
        <div class="k-bento-tile__label">Description</div>
        <p class="small mb-0">{{ job.description || "No description provided." }}</p>
      </div>

      <div class="k-bento-tile k-bento-span-12">
        <div class="k-toolbar">
          <input v-model="appQuery" class="form-control form-control-sm" placeholder="Search by name or email..." />
          <select v-model="statusFilter" class="form-select form-select-sm" style="max-width: 160px">
            <option value="all">All statuses</option>
            <option value="applied">Applied</option>
            <option value="shortlisted">Shortlisted</option>
            <option value="selected">Selected</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>

        <div class="table-responsive">
          <table class="table table-hover table-sm k-table mb-0">
            <thead>
              <tr>
                <th>Student</th>
                <th>Email</th>
                <th>CGPA</th>
                <th>Resume</th>
                <th>Status</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!appItems.length">
                <td colspan="6" class="text-muted text-center py-4">No applicants match this filter.</td>
              </tr>
              <tr
                v-for="app in appItems"
                :key="app.id"
                class="k-click-row"
                :class="{ 'k-click-row--active': selectedApp?.id === app.id }"
                @click="openApplicant(app)"
              >
                <td class="fw-medium">{{ app.student?.full_name }}</td>
                <td>{{ app.student?.user?.email }}</td>
                <td>{{ app.student?.cgpa ?? "-" }}</td>
                <td>
                  <span v-if="app.student?.resume_path" class="badge bg-light text-dark border">Uploaded</span>
                  <span v-else class="badge bg-light text-muted border">No resume</span>
                </td>
                <td><StatusBadge :status="app.status" /></td>
                <td class="text-end text-nowrap" @click.stop>
                  <button class="btn btn-sm btn-info me-1" @click="openShortlist(app.id)">Shortlist</button>
                  <button class="btn btn-sm btn-success me-1" @click="openSelect(app.id)">Select</button>
                  <button class="btn btn-sm btn-danger" @click="setStatus(app.id, 'rejected')">Reject</button>
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

    <CompanyApplicantModal
      v-if="selectedApp"
      :app="selectedApp"
      :resume-url="resumeUrl"
      :resume-is-pdf="resumeIsPdf"
      :resume-loading="resumeLoading"
      :resume-error="resumeError"
      @close="closeApplicant"
      @shortlist="openShortlist"
      @select="openSelect"
      @reject="(id) => setStatus(id, 'rejected')"
      @open-resume="openResumeExternal"
    />

    <CompanyShortlistModal
      :open="shortlistModal.open"
      :interview-at="shortlistModal.interview_at"
      :interview-notes="shortlistModal.interview_notes"
      @close="shortlistModal.open = false"
      @confirm="confirmShortlist"
      @update:interview-at="shortlistModal.interview_at = $event"
      @update:interview-notes="shortlistModal.interview_notes = $event"
    />

    <CompanySelectModal
      :open="selectModal.open"
      :salary="selectModal.salary"
      :joining-date="selectModal.joining_date"
      @close="selectModal.open = false"
      @confirm="confirmSelect"
      @update:salary="selectModal.salary = $event"
      @update:joining-date="selectModal.joining_date = $event"
    />
  </div>
</template>
