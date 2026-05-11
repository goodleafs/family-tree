<template>
  <div class="g-input" :class="{ 'has-error': error, 'is-disabled': disabled }">
    <label class="input-label" v-if="label" :for="inputId">
      {{ label }}
      <span class="required" v-if="required">*</span>
    </label>
    <div class="input-wrapper">
      <span class="input-prefix" v-if="$slots.prefix">
        <slot name="prefix" />
      </span>
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        class="input-field"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @focus="$emit('focus', $event)"
        @blur="$emit('blur', $event)"
      />
      <span class="input-suffix" v-if="$slots.suffix">
        <slot name="suffix" />
      </span>
    </div>
    <p class="input-error" v-if="error">{{ error }}</p>
    <p class="input-hint" v-else-if="hint">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

defineProps<{
  modelValue: string
  label?: string
  type?: string
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  error?: string
  hint?: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
  'focus': [event: FocusEvent]
  'blur': [event: FocusEvent]
}>()

const inputId = computed(() => `input-${Math.random().toString(36).slice(2, 9)}`)
</script>

<style scoped>
.g-input {
  margin-bottom: var(--space-4);
}

.input-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.required {
  color: var(--cinnabar);
  margin-left: 2px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-field {
  flex: 1;
  width: 100%;
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-base);
  font-family: var(--font-body);
  color: var(--text-primary);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.input-field::placeholder {
  color: var(--text-tertiary);
}

.input-field:hover:not(:disabled) {
  border-color: var(--border-secondary);
}

.input-field:focus {
  outline: none;
  border-color: var(--cinnabar);
  box-shadow: 0 0 0 3px var(--cinnabar-pale);
}

.input-prefix,
.input-suffix {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 var(--space-3);
  color: var(--text-tertiary);
}

.input-prefix {
  position: absolute;
  left: 0;
}

.input-prefix + .input-field {
  padding-left: calc(var(--space-3) * 2 + 16px);
}

.input-suffix {
  position: absolute;
  right: 0;
}

.has-error .input-field {
  border-color: var(--cinnabar);
}

.has-error .input-field:focus {
  box-shadow: 0 0 0 3px var(--cinnabar-pale);
}

.is-disabled .input-field {
  background: var(--bg-secondary);
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.input-error {
  margin: var(--space-1) 0 0;
  font-size: var(--text-sm);
  color: var(--cinnabar);
}

.input-hint {
  margin: var(--space-1) 0 0;
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}
</style>