<script setup>
/**
 * Detail modals for student, company, and drive rows clicked on admin tables.
 */
import StatusBadge from "../../components/StatusBadge.vue";

defineProps({
  detailLoading: { type: Boolean, default: false },
  studentDetail: { type: Object, default: null },
  companyDetail: { type: Object, default: null },
  driveDetail: { type: Object, default: null },
});

const emit = defineEmits(["close"]);
</script>

<template>
  <div>
    <div v-if="detailLoading" class="modal d-block" style="background: rgba(35, 36, 40, 0.35)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content p-4 text-center text-muted">Loading details...</div>
      </div>
    </div>

    <!-- Student detail -->
    <div
      v-if="studentDetail"
      class="modal d-block"
      style="background: rgba(35, 36, 40, 0.55)"
      @click.self="emit('close')"
    >
      <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <div>
              <h5 class="modal-title mb-0">{{ studentDetail.student.full_name }}</h5>
              <div class="small text-muted">{{ studentDetail.student.user?.email }}</div>
            </div>
            <button type="button" class="btn-close" aria-label="Close" @click="emit('close')" />
          </div>
          <div class="modal-body">
            <dl class="k-detail-list mb-4">
              <div><dt>Username</dt><dd>{{ studentDetail.student.user?.username || "-" }}</dd></div>
              <div><dt>Phone</dt><dd>{{ studentDetail.student.phone || "-" }}</dd></div>
              <div><dt>CGPA</dt><dd>{{ studentDetail.student.cgpa ?? "-" }}</dd></div>
              <div><dt>Year</dt><dd>{{ studentDetail.student.graduation_year ?? "-" }}</dd></div>
              <div><dt>Skills</dt><dd>{{ studentDetail.student.skills || "-" }}</dd></div>
              <div><dt>Resume</dt><dd>{{ studentDetail.student.resume_path || "Not uploaded" }}</dd></div>
            </dl>
            <h6 class="mb-2">Drives applied to</h6>
            <div class="table-responsive">
              <table class="table table-sm k-table mb-0">
                <thead>
                  <tr>
                    <th>Drive</th>
                    <th>Company</th>
                    <th>Status</th>
                    <th>Applied</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="!studentDetail.applications?.length">
                    <td colspan="4" class="text-muted text-center py-3">No applications yet.</td>
                  </tr>
                  <tr v-for="app in studentDetail.applications" :key="app.id">
                    <td>{{ app.job_position?.title }}</td>
                    <td>{{ app.job_position?.company?.name }}</td>
                    <td><StatusBadge :status="app.status" /></td>
                    <td class="small text-muted">{{ app.applied_at || "-" }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Company detail -->
    <div
      v-if="companyDetail"
      class="modal d-block"
      style="background: rgba(35, 36, 40, 0.55)"
      @click.self="emit('close')"
    >
      <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <div>
              <h5 class="modal-title mb-0">{{ companyDetail.company.name }}</h5>
              <StatusBadge :status="companyDetail.company.approval_status" class="mt-1" />
            </div>
            <button type="button" class="btn-close" aria-label="Close" @click="emit('close')" />
          </div>
          <div class="modal-body">
            <dl class="k-detail-list mb-3">
              <div><dt>Email</dt><dd>{{ companyDetail.company.user?.email || "-" }}</dd></div>
              <div><dt>Industry</dt><dd>{{ companyDetail.company.industry || "-" }}</dd></div>
              <div><dt>Website</dt><dd>{{ companyDetail.company.website || "-" }}</dd></div>
              <div><dt>HR contact</dt><dd>{{ companyDetail.company.hr_contact || "-" }}</dd></div>
            </dl>
            <div class="d-flex flex-wrap gap-3 mb-3 small">
              <span><strong>{{ companyDetail.stats.total_drives }}</strong> drives</span>
              <span><strong>{{ companyDetail.stats.total_applications }}</strong> applications</span>
              <span><strong>{{ companyDetail.stats.total_selected }}</strong> selected</span>
            </div>
            <h6 class="mb-2">Drives</h6>
            <div class="table-responsive">
              <table class="table table-sm k-table mb-0">
                <thead>
                  <tr>
                    <th>Drive</th>
                    <th>Status</th>
                    <th>Approval</th>
                    <th>Apps</th>
                    <th>Short</th>
                    <th>Selected</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="!companyDetail.drives?.length">
                    <td colspan="6" class="text-muted text-center py-3">No drives yet.</td>
                  </tr>
                  <tr v-for="d in companyDetail.drives" :key="d.id">
                    <td>{{ d.title }}</td>
                    <td><StatusBadge :status="d.status" /></td>
                    <td><StatusBadge :status="d.approval_status" /></td>
                    <td>{{ d.stats.total_applications }}</td>
                    <td>{{ d.stats.shortlisted }}</td>
                    <td>{{ d.stats.selected }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Drive detail -->
    <div
      v-if="driveDetail"
      class="modal d-block"
      style="background: rgba(35, 36, 40, 0.55)"
      @click.self="emit('close')"
    >
      <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <div>
              <h5 class="modal-title mb-0">{{ driveDetail.job_position.title }}</h5>
              <div class="small text-muted">{{ driveDetail.job_position.company?.name }}</div>
            </div>
            <button type="button" class="btn-close" aria-label="Close" @click="emit('close')" />
          </div>
          <div class="modal-body">
            <div class="d-flex flex-wrap gap-2 mb-3">
              <StatusBadge :status="driveDetail.job_position.status" />
              <StatusBadge :status="driveDetail.job_position.approval_status" />
            </div>
            <p class="small mb-2" style="white-space: pre-wrap">
              {{ driveDetail.job_position.description || "No description." }}
            </p>
            <div class="d-flex flex-wrap gap-3 mb-3 small">
              <span><strong>{{ driveDetail.stats.total_applications }}</strong> apps</span>
              <span><strong>{{ driveDetail.stats.applied }}</strong> applied</span>
              <span><strong>{{ driveDetail.stats.shortlisted }}</strong> shortlisted</span>
              <span><strong>{{ driveDetail.stats.selected }}</strong> selected</span>
              <span><strong>{{ driveDetail.stats.rejected }}</strong> rejected</span>
            </div>
            <h6 class="mb-2">Applicants</h6>
            <div class="table-responsive">
              <table class="table table-sm k-table mb-0">
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>Email</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="!driveDetail.applications?.length">
                    <td colspan="3" class="text-muted text-center py-3">No applicants yet.</td>
                  </tr>
                  <tr v-for="app in driveDetail.applications" :key="app.id">
                    <td>{{ app.student?.full_name }}</td>
                    <td>{{ app.student?.user?.email }}</td>
                    <td><StatusBadge :status="app.status" /></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
