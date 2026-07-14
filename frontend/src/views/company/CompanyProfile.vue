<script setup>
// company profile fields
import { onMounted, reactive, ref } from "vue";
import { api } from "../../api/client";
import StatusBadge from "../../components/StatusBadge.vue";
import { pushToast } from "../../services/toast";

const company = ref(null);
const loading = ref(true);
const profile = reactive({
  name: "",
  website: "",
  hr_contact: "",
  industry: "",
});

function showMsg(text, type = "success") {
  pushToast(text, type);
}

async function load() {
  loading.value = true;
  try {
    const data = await api("/api/company/profile");
    company.value = data.company;
    Object.assign(profile, {
      name: data.company.name || "",
      website: data.company.website || "",
      hr_contact: data.company.hr_contact || "",
      industry: data.company.industry || "",
    });
  } catch (e) {
    showMsg(e.message, "danger");
  } finally {
    loading.value = false;
  }
}

async function saveProfile() {
  try {
    const data = await api("/api/company/profile", {
      method: "PUT",
      body: JSON.stringify(profile),
    });
    company.value = data.company;
    showMsg("Profile saved");
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
        <div class="k-bento-tile__label">Company profile</div>
        <h1 class="k-page-title text-white mb-2">{{ profile.name || "Your company" }}</h1>
        <StatusBadge v-if="company" :status="company.approval_status" />
        <p v-if="company?.user" class="k-page-subtitle mb-0 mt-2">{{ company.user.email }}</p>
      </div>

      <div class="k-bento-tile k-bento-span-8">
        <h2 class="k-bento-tile__title">Details</h2>
        <div class="vstack gap-2">
          <label class="form-label mb-0">Company name</label>
          <input v-model="profile.name" class="form-control" placeholder="Company name" />
          <label class="form-label mb-0">Website</label>
          <input v-model="profile.website" class="form-control" placeholder="https://..." />
          <label class="form-label mb-0">HR contact</label>
          <input v-model="profile.hr_contact" class="form-control" placeholder="HR contact" />
          <label class="form-label mb-0">Industry</label>
          <input v-model="profile.industry" class="form-control" placeholder="Industry" />
          <button class="btn btn-primary align-self-start mt-2" @click="saveProfile">Save profile</button>
        </div>
      </div>

      <div class="k-bento-tile k-bento-tile--sky k-bento-span-4">
        <h2 class="k-bento-tile__title">Note</h2>
        <p class="small mb-0">
          Approval status is managed by the admin. Updating your profile does not change approval.
        </p>
      </div>
    </div>
  </div>
</template>
