<template>
  <button
    :class="['btn', `btn-${variant}`, `btn-${size}`, { 'btn-loading': loading, 'btn-block': block }]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span class="btn-spinner" v-if="loading">
      <svg viewBox="0 0 16 16" fill="none">
        <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2" opacity="0.25"/>
        <path d="M8 2a6 6 0 016 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </span>
    <span class="btn-content" v-else>
      <slot />
    </span>
  </button>
</template>

<script setup lang="ts">
defineProps<{
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
  block?: boolean
}>()

defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-family: var(--font-body);
  font-weight: var(--font-medium);
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 尺寸 */
.btn-sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-sm);
}

.btn-md {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
}

.btn-lg {
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-base);
}

/* 变体 */
.btn-primary {
  background: var(--cinnabar);
  color: white;
  border-color: var(--cinnabar);
}

.btn-primary:hover:not(:disabled) {
  background: var(--cinnabar-dark);
  border-color: var(--cinnabar-dark);
}

.btn-secondary {
  background: var(--indigo);
  color: white;
  border-color: var(--indigo);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--indigo-dark);
  border-color: var(--indigo-dark);
}

.btn-outline {
  background: transparent;
  color: var(--text-primary);
  border-color: var(--border-secondary);
}

.btn-outline:hover:not(:disabled) {
  border-color: var(--cinnabar);
  color: var(--cinnabar);
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
}

.btn-ghost:hover:not(:disabled) {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-danger {
  background: var(--cinnabar);
  color: white;
  border-color: var(--cinnabar);
}

.btn-danger:hover:not(:disabled) {
  background: var(--cinnabar-dark);
}

/* 块级 */
.btn-block {
  width: 100%;
}

/* 加载 */
.btn-spinner {
  display: flex;
  animation: spin 1s linear infinite;
}

.btn-spinner svg {
  width: 16px;
  height: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>