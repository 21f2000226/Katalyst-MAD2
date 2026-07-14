<script setup>
// left navbar for student/company. 
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const links = computed(() => {
  const matched = [...route.matched].reverse();
  for (const record of matched) {
    if (record.meta?.sidebarLinks) return record.meta.sidebarLinks;
  }
  return [];
});
</script>

<template>
  <div class="k-shell">
    <aside class="k-sidebar">
      <nav class="k-sidebar-nav">
        <router-link
          v-for="link in links"
          :key="link.to"
          class="k-sidebar-link"
          :to="link.to"
          active-class="is-active"
        >
        
          {{ link.label }}
        </router-link>
      </nav>
    </aside>
    <div class="k-shell-main">
      <router-view />
    </div>
  </div>
</template>
