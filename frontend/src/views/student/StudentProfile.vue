<script setup>
// student profile and resume uploadi
import { computed, onMounted, reactive, ref } from "vue";
import { api, openAuthedFile } from "../../api/client";
import { pushToast } from "../../services/toast";

const student = ref(null);
const loading = ref(true);
const resumeBusy = ref(false);
const resumeFile = ref(null);

const profile = reactive({

  full_name: "",
  phone: "",
  cgpa: "",
  graduation_year: "",
  skills: "",
  notify_deadlines: true,
});

const hasResume = computed(() => Boolean(student.value?.resume_path));


function showMsg(text, type = "success") {

  pushToast(text, type);
}

async function load() {

  loading.value = true;
  try {
    const data = await api("/api/student/profile");
    student.value = data.student;
    Object.assign(profile, {
      full_name: data.student.full_name || "",
      phone: data.student.phone || "",
      cgpa: data.student.cgpa ?? "",
      graduation_year: data.student.graduation_year ?? "",
      skills: data.student.skills || "",
      notify_deadlines: data.student.notify_deadlines !== false,
    });
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    loading.value = false;
  }
}


async function saveProfile() {
  try {
    const data = await api("/api/student/profile", {
      method: "PUT",
      body: JSON.stringify(profile),
    });
    student.value = data.student;
    showMsg("Profile saved");
  } catch (e) {
    showMsg(e.message, "danger");
  }
}


async function uploadResume() {
  if (!resumeFile.value?.files?.[0]) {
    showMsg("Choose a PDF or Word file first.", "warning");
    return;
  }
  const fd = new FormData();
  fd.append("resume", resumeFile.value.files[0]);
  resumeBusy.value = true;

  try {
    await api("/api/student/resume", { method: "POST", body: fd });
    showMsg("Resume uploaded and saved on the server.");
    resumeFile.value.value = "";
    await load();
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    resumeBusy.value = false;
  }
}


async function deleteResume() {

  if (!confirm("Delete your uploaded resume?")) return;
  
  try {
    await api("/api/student/resume", { method: "DELETE" });
    showMsg("Resume deleted");
    await load();
  } catch (e) {
    showMsg(e.message, "danger");
  }
}

onMounted(load);

</script>

<template>
  <div>
    <div v-if="loading" class="text-muted py-5 text-center">Loading profile...</div>
    <div v-else class="k-bento">
      <div class="k-bento-tile k-bento-tile--ink k-bento-span-12">
        <div class="k-bento-tile__label">Profile</div>
        <h1 class="k-page-title text-white mb-0">{{ profile.full_name || "Your profile" }}</h1>
        <p v-if="student?.user" class="k-page-subtitle mb-0 mt-1">{{ student.user.email }}</p>
      </div>

      <div class="k-bento-tile k-bento-span-6">
        <h2 class="k-bento-tile__title">Details</h2>

        <div class="vstack gap-2">
          <input v-model="profile.full_name" class="form-control" placeholder="Full name" />
          <input v-model="profile.phone" class="form-control" placeholder="Phone" />
          <input v-model="profile.cgpa" class="form-control" placeholder="CGPA" />
          <input v-model="profile.graduation_year" class="form-control" placeholder="Graduation year" />
          <input v-model="profile.skills" class="form-control" placeholder="Skills (comma separated)" />

          <div class="form-check mt-1">
            <input
              id="notifyDeadlines"
              v-model="profile.notify_deadlines"
              class="form-check-input"
              type="checkbox"
            />
            <label class="form-check-label" for="notifyDeadlines">
              Email me daily about upcoming drive deadlines
            </label>
          </div>

          <button class="btn btn-primary align-self-start" @click="saveProfile">Save profile</button>
        </div>

      </div>

      <div class="k-bento-tile k-bento-span-6">
        <h2 class="k-bento-tile__title">Resume</h2>
        <p class="small text-muted mb-3">
          PDF or Word file, stored locally on the server for company review.
        </p>
        <div v-if="hasResume" class="alert alert-success py-2 small mb-3">
          On file: <strong>{{ student.resume_path }}</strong>
        </div>
        
        <div v-else class="alert alert-warning py-2 small mb-3">
          No resume yet. Companies will see "No resume" until you upload one.
        </div>
        
        <input ref="resumeFile" type="file" class="form-control mb-3" accept=".pdf,.doc,.docx" />
        <div class="d-flex flex-wrap gap-2">
          <button class="btn btn-primary" :disabled="resumeBusy" @click="uploadResume">
            {{ resumeBusy ? "Uploading..." : "Upload resume" }}
          </button>
          <button
            v-if="hasResume"
            class="btn btn-outline-secondary"
            @click="openAuthedFile('/api/student/resume')"
          >
            View
          </button>
          <button v-if="hasResume" class="btn btn-outline-danger" @click="deleteResume">Delete</button>
        
        </div>
      </div>
    </div>
  </div>
</template>
