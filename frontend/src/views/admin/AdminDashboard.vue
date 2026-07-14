<script setup>
/**
 * Admin dashboard shell - loads data, tabs, and wires child tab/modal components.
 * click on rows for detail modals; add more records 
 */
import { computed, onMounted, reactive, ref } from "vue";
import { usePagedList } from "../../composables/usePagedList";
import { api } from "../../api/client";
import AdminAddPanel from "./AdminAddPanel.vue";
import { pushToast } from "../../services/toast";
import { runAdminCeleryJob } from "./adminCeleryJobs";
import AdminCompaniesTab from "./AdminCompaniesTab.vue";
import AdminPlacementsTab from "./AdminPlacementsTab.vue";
import AdminDetailModals from "./AdminDetailModals.vue";
import AdminDrivesTab from "./AdminDrivesTab.vue";
import AdminTabNav from "./AdminTabNav.vue";
import AdminPendingTab from "./AdminPendingTab.vue";
import AdminStatsRow from "./AdminStatsRow.vue";
import AdminStudentsTab from "./AdminStudentsTab.vue";

const data = ref(null);
const loading = ref(true);
const jobBusy = ref(false);
const activeTab = ref("pending");
const detailLoading = ref(false);
const studentDetail = ref(null);
const companyDetail = ref(null);

const driveDetail = ref(null);

const addKind = ref(null);
const showAddModal = ref(false);

const studentsSrc = computed(() => data.value?.students || []);
const companiesSrc = computed(() => data.value?.companies || []);

const jobsSrc = computed(() => data.value?.job_positions || []);
const placements = ref([]);
const placementsLoading = ref(false);

const {
  query: studentQuery,
  page: studentPage,
  pageItems: studentItems,
  filtered: studentFiltered,
  totalPages: studentPages,
  prev: studentPrev,
  next: studentNext,
  go: studentGo,
} = usePagedList(studentsSrc, {
  pageSize: 8,
  filterFn: (s, q) => {

    if (!q) return true;
    const hay = `${s.full_name || ""} ${s.user?.email || ""} ${s.user?.username || ""}`.toLowerCase();
    return hay.includes(q);

  },
});

const {
  query: companyQuery,
  page: companyPage,
  pageItems: companyItems,
  filtered: companyFiltered,
  totalPages: companyPages,
  prev: companyPrev,
  next: companyNext,
  go: companyGo,
} = usePagedList(companiesSrc, {

  pageSize: 8,
  filterFn: (c, q) => {
    if (!q) return true;
    const hay = `${c.name || ""} ${c.industry || ""} ${c.approval_status || ""}`.toLowerCase();
    return hay.includes(q);

  },
});

const {
  query: jobQuery,
  page: jobPage,
  pageItems: jobItems,
  filtered: jobFiltered,
  totalPages: jobPages,
  prev: jobPrev,
  next: jobNext,
  go: jobGo,
} = usePagedList(jobsSrc, {

  pageSize: 8,
  filterFn: (j, q) => {
    if (!q) return true;
    const hay = `${j.title || ""} ${j.company?.name || ""} ${j.status || ""} ${j.approval_status || ""}`.toLowerCase();
    return hay.includes(q);

  },
});

const newStudent = reactive({
  username: "",
  email: "",
  password: "",
  full_name: "",
  phone: "",
  cgpa: "",
  graduation_year: "",
  skills: "",
});

const newCompany = reactive({
  username: "",
  email: "",
  password: "",
  company_name: "",
  website: "",
  hr_contact: "",
  industry: "",

});

const newJob = reactive({

  company_id: "",
  title: "",
  description: "",
  requirements: "",
  min_cgpa: "",
  salary_min: "",
  salary_max: "",
  deadline: "",

});

async function load() {
  loading.value = true;

  try {
    data.value = await api("/api/admin/dashboard");
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    loading.value = false;
  }

}

async function loadPlacements() {

  placementsLoading.value = true;

  try {
    const res = await api("/api/admin/placements");
    placements.value = res.placements || [];
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    placementsLoading.value = false;
  }

}

function openTab(tab) {
  
  activeTab.value = tab;
  if (tab === "placements" && !placements.value.length) {
    loadPlacements();
  }

}

function showMsg(text, type = "success") {
  
  pushToast(text, type);

}

async function act(method, path, okText) {
  try {
    await api(path, { method });
    showMsg(okText);
    await load();
  } catch (e) {
    showMsg(e.message, "danger");
  }
}

// Child tabs emit { method, path, okText } so approve/blacklist stay in one place.
function onAct(payload) {
  act(payload.method, payload.path, payload.okText);
}

function closeDetails() {
  studentDetail.value = null;
  companyDetail.value = null;
  driveDetail.value = null;
}

async function openStudent(id) {
  closeDetails();
  detailLoading.value = true;
  try {
    studentDetail.value = await api(`/api/admin/students/${id}`);
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    detailLoading.value = false;
  }
}

async function openCompany(id) {
  closeDetails();
  detailLoading.value = true;
  try {
    companyDetail.value = await api(`/api/admin/companies/${id}`);
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    detailLoading.value = false;
  }
}

async function openDrive(id) {
  closeDetails();
  detailLoading.value = true;
  try {
    driveDetail.value = await api(`/api/admin/job-positions/${id}`);
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    detailLoading.value = false;
  }
}

function chooseAdd(kind) {
  addKind.value = kind;
  showAddModal.value = true;
}

function closeAddModal() {
  showAddModal.value = false;
  addKind.value = null;
}

async function addStudent() {
  try {
    await api("/api/admin/students", { method: "POST", body: JSON.stringify(newStudent) });
    showMsg("Student added");
    Object.assign(newStudent, {
      username: "",
      email: "",
      password: "",
      full_name: "",
      phone: "",
      cgpa: "",
      graduation_year: "",
      skills: "",
    });
    closeAddModal();
    await load();
  } catch (e) {
    showMsg(e.message, "danger");
  }
}

async function addCompany() {

  try {
    await api("/api/admin/companies", { method: "POST", body: JSON.stringify(newCompany) });
    showMsg("Company added");
    Object.assign(newCompany, {
      username: "",
      email: "",
      password: "",
      company_name: "",
      website: "",
      hr_contact: "",
      industry: "",
    });
    closeAddModal();
    await load();

  } catch (e) {
    showMsg(e.message, "danger");
  }
}

async function addJob() {
  try {

    await api("/api/admin/job-positions", { method: "POST", body: JSON.stringify(newJob) });
    showMsg("Drive created");
    Object.assign(newJob, {
      company_id: "",
      title: "",
      description: "",
      requirements: "",
      min_cgpa: "",
      salary_min: "",
      salary_max: "",

      deadline: "",

    });
    closeAddModal();
    await load();
  } catch (e) {
    showMsg(e.message, "danger");
  }
}

async function runCeleryJob(path, okText) {

  jobBusy.value = true;
  try {
    await runAdminCeleryJob(path, okText, showMsg);
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    jobBusy.value = false;
  }

}

const pendingCompanyCount = computed(() => data.value?.pending_companies?.length || 0);
const pendingJobCount = computed(() => data.value?.pending_job_positions?.length || 0);

onMounted(load);

</script>

<template>
  <div class="container-fluid py-4 px-3 px-lg-4">
    <div class="k-page-header">
      <div>
        <h1 class="k-page-title">Admin Dashboard</h1>
        <p class="k-page-subtitle mb-0">Manage students, companies, and placement drives</p>
      </div>

      <div class="btn-group btn-group-sm">
        <button
          class="btn btn-outline-secondary"
          :disabled="jobBusy"
          @click="runCeleryJob('/api/jobs/admin/daily-reminders', 'Daily reminders queued.')"
        >

          Run daily reminders
        </button>
        <button
          class="btn btn-outline-secondary"
          :disabled="jobBusy"
          @click="runCeleryJob('/api/jobs/admin/monthly-report', 'Monthly report queued.')"
        >
          Run monthly report

        </button>
      </div>
    </div>

    <div v-if="loading" class="text-muted py-5 text-center">Loading dashboard...</div>
    <template v-else-if="data">

      <AdminStatsRow :stats="data.stats" />
      <AdminTabNav
        :active-tab="activeTab"
        :pending-count="pendingCompanyCount + pendingJobCount"
        @open-tab="openTab"
      />


      <AdminPendingTab
        v-show="activeTab === 'pending'"
        :pending-companies="data.pending_companies"
        :pending-jobs="data.pending_job_positions"
        @open-company="openCompany"
        @open-drive="openDrive"
        @act="onAct"
      />

      <AdminStudentsTab
        v-show="activeTab === 'students'"
        :items="studentItems"
        :query="studentQuery"
        :page="studentPage"
        :total-pages="studentPages"
        :total-items="studentFiltered.length"
        @update:query="studentQuery = $event"
        @open="openStudent"
        @act="onAct"
        @prev="studentPrev"
        @next="studentNext"
        @go="studentGo"
      />

      
      <AdminCompaniesTab
        v-show="activeTab === 'companies'"
        :items="companyItems"
        :query="companyQuery"
        :page="companyPage"
        :total-pages="companyPages"
        :total-items="companyFiltered.length"
        @update:query="companyQuery = $event"
        @open="openCompany"
        @act="onAct"
        @prev="companyPrev"
        @next="companyNext"
        @go="companyGo"
      />

      <AdminDrivesTab
        v-show="activeTab === 'jobs'"
        :items="jobItems"
        :query="jobQuery"
        :page="jobPage"
        :total-pages="jobPages"
        :total-items="jobFiltered.length"
        @update:query="jobQuery = $event"
        @open="openDrive"
        @act="onAct"
        @prev="jobPrev"
        @next="jobNext"
        @go="jobGo"
      />

      <AdminPlacementsTab
        v-show="activeTab === 'placements'"
        :placements="placements"
        :loading="placementsLoading"
        @refresh="loadPlacements"
      />

      <!-- Keep mounted while the add modal is open so the form is not hidden mid-edit -->
      <AdminAddPanel
        v-show="activeTab === 'add' || showAddModal"
        :show-modal="showAddModal"
        :add-kind="addKind"
        :new-student="newStudent"
        :new-company="newCompany"
        :new-job="newJob"
        @choose="chooseAdd"
        @close="closeAddModal"
        @save-student="addStudent"
        @save-company="addCompany"
        @save-job="addJob"
      />
    </template>

    <AdminDetailModals
      :detail-loading="detailLoading"
      :student-detail="studentDetail"
      :company-detail="companyDetail"
      :drive-detail="driveDetail"
      @close="closeDetails"
    />
  </div>
</template>
