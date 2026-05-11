<template>
  <div class="g-card" :class="{ 'g-card-hoverable': hoverable }">
    <div class="card-header" v-if="$slots.header || title">
      <slot name="header">
        <h3 class="card-title" v-if="title">{{ title }}</h3>
      </slot>
      <div class="card-actions" v-if="$slots.actions">
        <slot name="actions" />
      </div>
    </div>
    <div class="card-body">
      <slot />
    </div>
    <div class="card-footer" v-if="$slots.footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  hoverable?: boolean
}>()
</script>

<style scoped>
.g-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-fast);
}

.g-card-hoverable:hover {
  border-color: var(--border-secondary);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  cursor: pointer;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-secondary);
}

.card-title {
  margin: 0;
  font-family: var(--font-title);
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  letter-spacing: 0.05em;
}

.card-actions {
  display: flex;
  gap: var(--space-2);
}

.card-body {
  padding: var(--space-5);
}

.card-footer {
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--border-primary);
  background: var(--bg-secondary);
}
</style>