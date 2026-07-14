<script setup>
/**
 * Applicant profile and  resume PDF preview modal for a single application. */
defineProps({
  app: { type: Object, required: true },
  resumeUrl: { type: String, default: "" },
  resumeIsPdf: { type: Boolean, default: false },
  resumeLoading: { type: Boolean, default: false },
  resumeError: { type: String, default: "" },
});


defineEmits(["close", "shortlist", "select", "reject", "open-resume"]);

</script>

<template>
  <div
    class="modal d-block"
    tabindex="-1"
    style="background: rgba(35, 36, 40, 0.55)"
    @click.self="$emit('close')"
  >
    <div class="modal-dialog modal-dialog-centered modal-xl modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <div>
            <h5 class="modal-title mb-0">{{ app.student?.full_name }}</h5>
            <div class="small text-muted">Application status: {{ app.status }}</div>
          </div>
          <button type="button" class="btn-close" aria-label="Close" @click="$emit('close')" />
        </div>
        <div class="modal-body">
          <div class="row g-4">
            <div class="col-lg-4">
              <h6 class="text-uppercase text-muted small fw-semibold mb-3">Student details</h6>
              <dl class="k-detail-list mb-4">
                <div>
                  <dt>Full name</dt>
                  <dd>{{ app.student?.full_name || "-" }}</dd>
                </div>
                <div>
                  <dt>Email</dt>
                  <dd>{{ app.student?.user?.email || "-" }}</dd>
                </div>
                <div>
                  <dt>Username</dt>
                  <dd>{{ app.student?.user?.username || "-" }}</dd>
                </div>
                <div>
                  <dt>Phone</dt>
                  <dd>{{ app.student?.phone || "-" }}</dd>
                </div>
                <div>
                  <dt>CGPA</dt>
                  <dd>{{ app.student?.cgpa ?? "-" }}</dd>
                </div>
                <div>
                  <dt>Graduation year</dt>
                  <dd>{{ app.student?.graduation_year ?? "-" }}</dd>
                </div>
                <div>
                  <dt>Skills</dt>
                  <dd>{{ app.student?.skills || "-" }}</dd>
                </div>
                <div>
                  <dt>Interview</dt>
                  <dd>
                    {{
                      app.interview_at ? app.interview_at.replace("T", " ").slice(0, 16) : "-"
                    }}
                  </dd>
                </div>
                <div>
                  <dt>Interview notes</dt>
                  <dd>{{ app.interview_notes || "-" }}</dd>
                </div>
                <div>
                  <dt>Applied at</dt>
                  <dd>{{ app.applied_at || "-" }}</dd>
                </div>
              </dl>

              <div class="d-flex flex-wrap gap-2">
                <button class="btn btn-sm btn-info" @click="$emit('shortlist', app.id)">Shortlist</button>
                <button class="btn btn-sm btn-success" @click="$emit('select', app.id)">Select</button>
                <button class="btn btn-sm btn-danger" @click="$emit('reject', app.id)">Reject</button>
              </div>

            </div>

            <div class="col-lg-8">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="text-uppercase text-muted small fw-semibold mb-0">Resume</h6>

                <button
                  v-if="app.student?.resume_path"
                  type="button"
                  class="btn btn-sm btn-outline-secondary"
                  @click="$emit('open-resume')"
                >

                  Open in new tab

                </button>
              </div>

              <div v-if="!app.student?.resume_path" class="k-empty py-5 border rounded">
                <div class="k-empty__title">No resume uploaded</div>
                <div class="k-empty__text">This student has not uploaded a resume yet.</div>
              </div>

              <div v-else-if="resumeLoading" class="text-muted py-5 text-center border rounded">
                Loading resume...
              </div>

              <div v-else-if="resumeError" class="alert alert-danger mb-0">{{ resumeError }}</div>

              <iframe
                v-else-if="resumeIsPdf && resumeUrl"
                class="k-pdf-frame"
                :src="resumeUrl"
                title="Student resume PDF"
              />

              <div v-else class="k-empty py-5 border rounded">
                <div class="k-empty__title">Preview not available</div>
                <div class="k-empty__text mb-3">
                  This file is not a PDF (or the browser cannot embed it). Open it in a new tab instead.
                </div>

                <button type="button" class="btn btn-sm btn-primary" @click="$emit('open-resume')">
                  Open resume
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
