<script setup>
// toast stack (mounted once in App.vue and shared, for those messages that come up and disappear after an action TTL = 10s)
import { toastState, removeToast } from "../services/toast";
</script>

<template>
  <div class="k-toast-host" aria-live="polite" aria-relevant="additions">
    <div
      v-for="t in toastState.items"
      :key="t.id"
      class="k-toast"
      :class="`k-toast--${t.type}`"
      role="status"
    >
      <span class="k-toast__text">{{ t.text }}</span>
      <button
        type="button"
        class="k-toast__close"
        aria-label="Dismiss"
        @click="removeToast(t.id)"
      >
        ×
      </button>
    </div>
  </div>
</template>
