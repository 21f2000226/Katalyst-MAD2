<script setup>
// collapsible tips 
import { onMounted, ref } from "vue";

const props = defineProps({
  title: { type: String, default: "Tip" },
  storageKey: { type: String, default: "" },
  variant: { type: String, default: "sky" },
});

const visible = ref(true);

onMounted(() => {
  if (props.storageKey && localStorage.getItem(props.storageKey) === "1") {
    visible.value = false;
  }
});

function dismiss() {
  visible.value = false;
  if (props.storageKey) {
    localStorage.setItem(props.storageKey, "1");
  }
}
</script>

<template>
  <div
    v-if="visible"
    class="k-bento-tile"
    :class="variant === 'sky' ? 'k-bento-tile--sky' : ''"
  >
    <div class="d-flex justify-content-between align-items-start gap-2 mb-2">
      <h2 class="k-bento-tile__title mb-0">{{ title }}</h2>
      <button
        type="button"
        class="btn-close btn-close-sm"
        aria-label="Close tip"
        @click="dismiss"
      />
    </div>
    <slot />
  </div>
</template>
