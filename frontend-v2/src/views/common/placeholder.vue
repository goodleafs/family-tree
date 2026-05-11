<template>
  <div class="placeholder-page">
    <div class="placeholder-content">
      <div class="placeholder-icon">{{ icon }}</div>
      <h1 class="placeholder-title">{{ title }}</h1>
      <p class="placeholder-desc">{{ desc }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon: string
  title: string
  desc: string
}>()
</script>

<style scoped>
.placeholder-page {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-content {
  text-align: center;
}

.placeholder-icon {
  font-size: 64px;
  margin-bottom: var(--space-4);
}

.placeholder-title {
  font-family: var(--font-title);
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2);
}

.placeholder-desc {
  font-size: var(--text-base);
  color: var(--text-tertiary);
  margin: 0;
}
</style>