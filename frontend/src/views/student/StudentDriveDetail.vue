<script setup>
 // modal for drive details before applying, also checks eligibility based on CGPA
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "../../api/client";
import StatusBadge from "../../components/StatusBadge.vue";
import { pushToast } from "../../services/toast";

const route = useRoute();
const router = useRouter();
const drive = ref(null);
const alreadyApplied = ref(false);
const eligible = ref(true);
const eligibilityMessage = ref("");
const studentCgpa = ref(null);
const loading = ref(true);
const applying = ref(false);

const salaryRange = computed(() => {
  if (!drive.value) return null;
  const min = drive.value.salary_min;
  const max = drive.value.salary_max;
  if (min == null && max == null) return null;
  if (min != null && max != null) return `${min} - ${max} LPA`;
  if (min != null) return `From ${min} LPA`;
  return `Up to ${max} LPA`;
});


function showMsg(text, type = "success") {
  pushToast(text, type);
}


async function load() {
  loading.value = true;

  try {
    const data = await api(`/api/student/job-positions/${route.params.id}`);
    drive.value = data.job_position;
    alreadyApplied.value = Boolean(data.already_applied);
    eligible.value = data.eligible !== false;
    eligibilityMessage.value = data.eligibility_message || "";
    studentCgpa.value = data.student_cgpa ?? null;
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    loading.value = false;
  }

}

async function apply() {

  if (!eligible.value) {
    showMsg(eligibilityMessage.value || "You are not eligible for this drive.", "warning");
    return;
  }

  applying.value = true;
  try {
    await api("/api/student/applications", {
      method: "POST",
      body: JSON.stringify({ job_position_id: Number(route.params.id) }),
    });
    showMsg("Application submitted");
    alreadyApplied.value = true;
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    applying.value = false;
  }

}

onMounted(load);
</script>

<template>
  <div>

    <div v-if="loading" class="text-muted py-5 text-center">Loading drive...</div>
    <div v-else-if="drive" class="k-bento">
      <div class="k-bento-tile k-bento-span-12 py-3">
        <button
          type="button"
          class="btn btn-link btn-sm px-0 text-decoration-none d-inline-flex align-items-center gap-2"
          @click="router.push('/student/drives')"
        >
          <span class="k-back-arrow" aria-hidden="true">←</span>
          Back to drives
        </button>
      </div>

      <div class="k-bento-tile k-bento-tile--ink k-bento-span-8">
        <div class="k-bento-tile__label">Placement drive</div>
        <h1 class="k-page-title text-white mb-2">{{ drive.title }}</h1>
        <p class="k-page-subtitle mb-0">{{ drive.company?.name }}</p>
      </div>

      <div class="k-bento-tile k-bento-tile--sky k-bento-span-4">
        <div class="k-bento-tile__label">Status</div>
        <div class="mb-2">
          <StatusBadge v-if="alreadyApplied" status="applied" />
          <span v-else class="badge bg-light text-dark border">Not applied</span>
        </div>
        <div class="small text-muted">Deadline</div>
        <div class="fw-semibold">{{ drive.deadline || "Not specified" }}</div>
      </div>

      <div class="k-bento-tile k-bento-span-8">
        <h2 class="k-bento-tile__title">About this drive</h2>
        <p class="mb-4" style="white-space: pre-wrap">{{ drive.description || "No description provided." }}</p>

        <h2 class="k-bento-tile__title">Eligibility</h2>
        <p class="mb-2">
          <strong>Minimum CGPA:</strong>
          {{ drive.min_cgpa != null ? drive.min_cgpa : "No cutoff" }}
          <span v-if="studentCgpa != null" class="text-muted"> (yours: {{ studentCgpa }})</span>
        </p>
        <p class="mb-0" style="white-space: pre-wrap">{{ drive.requirements || "No additional notes." }}</p>
      </div>

      <div class="k-bento-tile k-bento-span-4">
        <h2 class="k-bento-tile__title">Package</h2>
        <p class="mb-3">{{ salaryRange || "Not disclosed" }}</p>

        <div v-if="!alreadyApplied && !eligible" class="alert alert-warning py-2 small mb-3">
          {{ eligibilityMessage }}
        </div>

        <button
          v-if="!alreadyApplied"
          class="btn btn-primary w-100"
          :disabled="applying || !eligible"
          @click="apply"
        >
          {{ applying ? "Applying..." : eligible ? "Apply to this drive" : "Not eligible" }}
        </button>
        <button v-else class="btn btn-outline-secondary w-100" disabled>Already applied</button>
      </div>
    </div>
  </div>
  
</template>
