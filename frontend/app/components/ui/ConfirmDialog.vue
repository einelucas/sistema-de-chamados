<script setup lang="ts">
// Modal de confirmação reutilizável para ações destrutivas ou críticas.
const props = defineProps<{
  modelValue: boolean
  title: string
  message: string
  confirmLabel?: string
  danger?: boolean
  loading?: boolean
}>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean]; confirm: [] }>()
</script>

<template>
  <UiModal :model-value="modelValue" :title="title" @update:model-value="emit('update:modelValue', $event)">
    <p style="color: var(--color-text-muted); margin: 0">{{ message }}</p>
    <template #footer>
      <button class="btn btn-secondary" @click="emit('update:modelValue', false)">Cancelar</button>
      <button
        :class="['btn', danger ? 'btn-danger' : 'btn-primary']"
        :disabled="loading"
        @click="emit('confirm')"
      >
        {{ loading ? 'Aguarde...' : (confirmLabel || 'Confirmar') }}
      </button>
    </template>
  </UiModal>
</template>
