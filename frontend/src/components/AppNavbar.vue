<script setup>
// Top nav: logo, login/signup for guests, account menu when signed in.
import { computed } from "vue";
import { useRouter } from "vue-router";
import logoUrl from "../assets/Katalyst_Logo.png";
import { authState, dashboardPathForRole, logout } from "../services/auth";


const router = useRouter();
const user = computed(() => authState.user);


// Guests start on landing page '/'; signed-in users will directly go to their role dashboard.
const brandTo = computed(() => {
  if (user.value) return dashboardPathForRole(user.value.role);
  return "/";
});


const profileTo = computed(() => {
  if (user.value?.role === "student") return "/student/profile";
  if (user.value?.role === "company") return "/company/profile";
  return null;
});


function handleLogout() {
  logout();
  router.push("/");
}

</script>

<template>
  <nav class="navbar navbar-expand-lg k-navbar">
    <div class="container-fluid px-3 px-lg-4">
      <router-link class="navbar-brand d-flex align-items-center" :to="brandTo">
        <img :src="logoUrl" alt="Katalyst" class="k-navbar-logo" />
      </router-link>
      <button
        class="navbar-toggler border-0"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto align-items-lg-center gap-1">
          <template v-if="user">
            <li class="nav-item dropdown">
              <a
                class="nav-link dropdown-toggle d-flex align-items-center gap-1"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >

                <span>{{ user.username }}</span>
                <span class="k-role-badge">{{ user.role }}</span>
              </a>
              <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0 mt-1">
                <li>
                  <span class="dropdown-item-text text-muted" style="font-size: 0.8rem">
                    {{ user.email }}
                  </span>

                </li>
                <li v-if="profileTo">
                  <router-link class="dropdown-item" :to="profileTo">Profile</router-link>
                </li>
                <li><hr class="dropdown-divider my-1" /></li>
                
                <li>
                  <button class="dropdown-item" type="button" @click="handleLogout">Log out</button>
                </li>
              </ul>
            </li>
          </template>

          <template v-else>
            <li class="nav-item">
              <router-link class="nav-link" to="/login">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/register" class="btn btn-primary btn-sm ms-1 px-3">Sign up</router-link>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>
