<script setup lang="ts">
defineProps<{ modelValue: boolean; title: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

function close() {
  emit('update:modelValue', false)
}
</script>

<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal-overlay" @click.self="close">
      <div class="modal-card">
        <div class="modal-header">
          <div class="modal-title">
            <span><UiIcon name="activity" :size="18" /></span>
            <h3>{{ title }}</h3>
          </div>
          <button class="modal-close" aria-label="Fechar" @click="close"><UiIcon name="close" :size="18" /></button>
        </div>
        <div class="modal-body"><slot /></div>
        <div v-if="$slots.footer" class="modal-footer"><slot name="footer" /></div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-card {
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  background: linear-gradient(180deg, var(--color-surface-soft), var(--color-surface));
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-lg);
  animation: modal-in var(--transition-base);
}
.modal-title {
  display: flex;
  align-items: center;
  gap: 11px;
}
.modal-title > span {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  color: var(--color-primary);
  background: var(--color-primary-light);
  border-radius: 10px;
}
.modal-close {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  border-radius: 10px;
  cursor: pointer;
}
.modal-close:hover { color: var(--color-primary); background: var(--color-primary-light); }
</style>
