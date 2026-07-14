<script setup>
//main entrypoint
import AppNavbar from "./components/AppNavbar.vue";
import ToastHost from "./components/ToastHost.vue";
</script>

<template>
  <AppNavbar />
  <main>
    <router-view />
  </main>
  <footer class="k-footer mt-auto">
    <div class="container">
      &copy; {{ new Date().getFullYear() }} Katalyst - Placement Portal
    </div>
  </footer>
  <ToastHost />
</template>
