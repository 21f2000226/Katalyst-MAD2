<script setup>
// login. errors go to toast
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { dashboardPathForRole, login } from "../services/auth";
import { pushToast } from "../services/toast";

const router = useRouter();
const route = useRoute();
const username = ref("");
const password = ref("");
const loading = ref(false);

async function submit() {
  loading.value = true;
  try {
    const user = await login(username.value, password.value);
    const redirect = route.query.redirect || dashboardPathForRole(user.role);
    router.push(redirect);
  } catch (e) {
    pushToast(e.message || "Login failed", "danger");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <!-- login card -->
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-12 col-md-8 col-lg-5">
        <div class="card shadow-sm border-0">
          <div class="card-body p-4 p-md-5">
            <h2 class="card-title mb-4">Login</h2>
            <form @submit.prevent="submit">
              <div class="mb-3">
                <label for="username" class="form-label">Username or Email</label>
                <input
                  id="username"
                  v-model="username"
                  type="text"
                  class="form-control"
                  required
                  placeholder="Enter username or email"
                  autocomplete="username"
                />
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input
                  id="password"
                  v-model="password"
                  type="password"
                  class="form-control"
                  required
                  placeholder="Enter password"
                  autocomplete="current-password"
                />
              </div>
              <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
                {{ loading ? "Signing in..." : "Sign in" }}
              </button>
            </form>
            <p class="mt-3 mb-0 text-center text-muted small">
              Don't have an account? <router-link to="/register">Sign up</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
