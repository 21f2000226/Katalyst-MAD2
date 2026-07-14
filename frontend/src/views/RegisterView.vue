<script setup>
// register a student or a company
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { register } from "../services/auth";
import { pushToast } from "../services/toast";

const route = useRoute();
const router = useRouter();

const role = ref(
  route.query.role === "company" || route.query.role === "student" ? route.query.role : null
);

const form = ref({
  username: "",
  email: "",
  password: "",
  password_confirm: "",
  full_name: "",
  phone: "",
  cgpa: "",
  graduation_year: "",
  skills: "",
  company_name: "",
  website: "",
  hr_contact: "",
  industry: "",
});
const loading = ref(false);

function chooseRole(nextRole) {
  role.value = nextRole;
}

async function submit() {
  loading.value = true;
  try {
    const payload = { role: role.value, ...form.value };
    await register(payload);
    pushToast("Registration successful. Please login.", "success");
    setTimeout(() => router.push("/login"), 1200);
  } catch (e) {
    pushToast(e.message || "Registration failed", "danger");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <!-- pick a role then fill the form -->
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-12 col-md-8 col-lg-6">
        <div class="card shadow-sm border-0">
          <div class="card-body p-4 p-md-5">
            <h2 class="card-title mb-4">Sign up</h2>
            <p class="text-muted small mb-4">
              Register as a Student or Company. Admin accounts are managed by the institute.
            </p>

            <div v-if="!role">
              <p class="mb-3">First, choose your role:</p>
              <div class="mb-3">
                <label class="form-label">I am a</label>
                <select class="form-select" :value="''" @change="chooseRole($event.target.value)">
                  <option value="" disabled selected>Choose role</option>
                  <option value="student">Student</option>
                  <option value="company">Company</option>
                </select>
              </div>
            </div>

            <form v-else @submit.prevent="submit">
              <p class="mb-3">
                Registering as <strong class="text-capitalize">{{ role }}</strong>.
                <button type="button" class="btn btn-link btn-sm p-0" @click="role = null">Change</button>
              </p>

              <div class="mb-3">
                <label class="form-label">Username</label>
                <input v-model="form.username" class="form-control" required placeholder="Choose a username" />
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input v-model="form.email" type="email" class="form-control" required placeholder="your@email.com" />
              </div>

              <hr class="my-4" />

              <template v-if="role === 'student'">
                <h5 class="mb-3">Student details</h5>
                <div class="mb-3">
                  <label class="form-label">Full Name</label>
                  <input v-model="form.full_name" class="form-control" required placeholder="Your full name" />
                </div>
                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label">Phone</label>
                    <input v-model="form.phone" class="form-control" placeholder="Phone number" />
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Graduation year</label>
                    <input v-model="form.graduation_year" type="number" class="form-control" placeholder="e.g. 2026" />
                  </div>
                </div>
                <div class="row g-3 mt-0">
                  <div class="col-md-6">
                    <label class="form-label">CGPA</label>
                    <input v-model="form.cgpa" type="number" step="0.01" class="form-control" placeholder="e.g. 8.50" />
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Skills</label>
                    <input v-model="form.skills" class="form-control" placeholder="python, sql, ml" />
                    <div class="form-text">Comma-separated.</div>
                  </div>
                </div>
              </template>

              <template v-else>
                <h5 class="mb-3">Company details</h5>
                <div class="mb-3">
                  <label class="form-label">Company name</label>
                  <input v-model="form.company_name" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Industry</label>
                  <input v-model="form.industry" class="form-control" />
                </div>
                <div class="mb-3">
                  <label class="form-label">Website</label>
                  <input v-model="form.website" class="form-control" />
                </div>
                <div class="mb-3">
                  <label class="form-label">HR contact</label>
                  <input v-model="form.hr_contact" class="form-control" />
                </div>
              </template>

              <hr class="my-4" />

              <div class="mb-3">
                <label class="form-label">Password</label>
                <input v-model="form.password" type="password" class="form-control" required minlength="6" />
              </div>
              <div class="mb-3">
                <label class="form-label">Confirm password</label>
                <input v-model="form.password_confirm" type="password" class="form-control" required />
              </div>

              <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
                {{ loading ? "Submitting..." : "Create account" }}
              </button>
            </form>

            <p class="mt-3 mb-0 text-center text-muted small">
              Already have an account? <router-link to="/login">Log in</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
