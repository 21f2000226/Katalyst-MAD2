<script setup>

defineProps({
  status: { type: String, required: true },
});

</script>

<template>
  <!-- coloured status pill selected/rejected etc, approved/pending for companies-->
  <span :class="['k-badge', `k-badge--${status || 'pending'}`]">{{ status }}</span>
</template>
