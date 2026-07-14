<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "../../api/client";
import ClosableTip from "../../components/ClosableTip.vue";
import TablePager from "../../components/TablePager.vue";
import { usePagedList } from "../../composables/usePagedList";
import { pushToast } from "../../services/toast";

const router = useRouter();
const data = ref(null);
const loading = ref(true);

const drivesSrc = computed(() => data.value?.available_job_positions || []);
const appliedIds = computed(() => data.value?.applied_job_position_ids || []);
//Browse open drives and apply for them 
const {
  query: driveQuery,
  page: drivePage,
  pageItems: driveItems,
  filtered: driveFiltered,
  totalPages: drivePages,
  prev: drivePrev,
  next: driveNext,
  go: driveGo,
} = usePagedList(drivesSrc, {
  pageSize: 6,
  filterFn: (drive, q) => {
    if (!q) return true;
    const hay = `${drive.title || ""} ${drive.company?.name || ""} ${drive.description || ""}`.toLowerCase();
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

onMounted(load);
</script>

<template>
  <div>
    <div v-if="loading" class="text-muted py-5 text-center">Loading drives...</div>
    <div v-else-if="data" class="k-bento">
      <div class="k-bento-tile k-bento-tile--ink k-bento-span-6">
        <div class="k-bento-tile__label">Student</div>
        <h1 class="k-page-title text-white mb-1">{{ data.student.full_name }}</h1>
        <p class="k-page-subtitle mb-0">Browse placement drives and open one to review before you apply.</p>
      </div>

      <div class="k-bento-span-6 k-bento-stats" style="grid-template-columns: repeat(2, minmax(0, 1fr))">
        <div class="k-bento-tile k-bento-tile--sky">
          <div class="k-bento-tile__label">Open drives</div>
          <div class="k-bento-tile__value">{{ data.available_job_positions?.length || 0 }}</div>
        </div>
        <div class="k-bento-tile k-bento-tile--sea" >
          <div class="k-bento-tile__label" >Applications</div>
          <div class="k-bento-tile__value" >{{ data.applications?.length || 0 }}</div>
        </div >
      </div>

      <div v-if="data.placement" class="k-bento-span-12">
        <div class="k-placement-banner">
          <div>
            <div class="fw-semibold">You are placed</div>
            <div class="small">
              Salary: {{ data.placement.salary }} LPA
              <span v-if="data.placement.joining_date"> · Joining: {{ data.placement.joining_date }}</span> 

            </div>
          </div>
        </div>
      </div>

      <div class="k-bento-tile k-bento-span-8">

        <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
          <h2 class="k-bento-tile__title mb-0">Open drives</h2>

          <input
            v-model="driveQuery"
            class="form-control form-control-sm"
            style="max-width: 240px"
            placeholder="Search drives..."
          />
          
        </div>
        <div v-if="!driveItems.length" class="k-empty py-4">
          <div class="k-empty__title">No drives found</div>
          <div class="k-empty__text">Try another search, or check back later.</div>
        </div>
        <div v-else class="row g-3">
          <div v-for="drive in driveItems" :key="drive.id" class="col-md-6">
            <button
              type="button"
              class="card k-card h-100 border-0 shadow-none w-100 text-start k-drive-card"
              style="background: rgba(200, 129, 58, .07)"
              @click="router.push(`/student/drives/${drive.id}`)"
            >
              <div class="card-body d-flex flex-column">
                <div class="d-flex justify-content-between align-items-start gap-2 mb-2">
                  <h3 class="h6 mb-0">{{ drive.title }}</h3>
                  <span v-if="appliedIds.includes(drive.id)" class="badge bg-secondary">Applied</span>
                </div>
                <p class="small text-muted mb-1">{{ drive.company?.name }}</p>
                <p class="small flex-grow-1 mb-2">
                  {{ (drive.description || "").slice(0, 100) }}{{ (drive.description || "").length > 100 ? "..." : "" }}
                </p>

                <div class="d-flex justify-content-between align-items-center mt-auto">
                  <span class="small text-muted">Deadline: {{ drive.deadline || "N/A" }}</span>
                  <span v-if="drive.min_cgpa != null" class="small text-muted">Min CGPA {{ drive.min_cgpa }}</span>
                  <span class="small text-primary fw-medium">View details →</span>
                </div>

              </div>
            </button>
          </div>
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

      <ClosableTip
        class="k-bento-span-4"
        title="Tip"
        storage-key="tip-student-drives"
      >
        <p class="small mb-3">
          Upload a resume from your Profile (account menu) so companies can open your CV when you apply.
        </p>
        <button type="button" class="btn btn-sm btn-accent" @click="router.push('/student/profile')">
          Go to profile
        </button>
      </ClosableTip>
    </div>
  </div>
</template>
