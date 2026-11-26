<script setup lang="ts">
import { CATEGORY_LABELS, PRIORITY_LABELS } from '~/types/request'
import type { RequestCategory, RequestPriority } from '~/types/request'

const props = defineProps<{
  initialTitle?: string
  initialDescription?: string
  initialCategory?: RequestCategory
  initialPriority?: RequestPriority
  initialDueDate?: string | null
  showPriority?: boolean
  loading?: boolean
  submitLabel?: string
}>()

const emit = defineEmits<{
  submit: [payload: { title: string; description: string; category: RequestCategory; priority: RequestPriority; due_date: string | null }]
}>()

const title = ref(props.initialTitle || '')
const description = ref(props.initialDescription || '')
const category = ref<RequestCategory>(props.initialCategory || 'TI')
const priority = ref<RequestPriority>(props.initialPriority || 'MEDIA')
const dueDate = ref(props.initialDueDate ? props.initialDueDate.slice(0, 10) : '')
const errors = ref<{ title?: string; description?: string }>({})

function validate(): boolean {
  errors.value = {}
  if (title.value.trim().length < 3) errors.value.title = 'O título deve ter ao menos 3 caracteres.'
  if (description.value.trim().length < 3) errors.value.description = 'Descreva a solicitação com mais detalhes.'
  return Object.keys(errors.value).length === 0
}

function handleSubmit() {
  if (!validate()) return
  emit('submit', {
    title: title.value.trim(),
    description: description.value.trim(),
    category: category.value,
    priority: priority.value,
    due_date: dueDate.value ? new Date(dueDate.value).toISOString() : null,
  })
}
</script>

<template>
  <form class="request-form" @submit.prevent="handleSubmit">
    <div class="form-intro">
      <span><UiIcon name="requests" :size="19" /></span>
      <div><h3>Informações da solicitação</h3><p>Preencha os dados necessários para o atendimento.</p></div>
    </div>

    <VTextField v-model="title" label="Título *" maxlength="200" :error-messages="errors.title" class="mb-4"/>

    <VTextarea v-model="description" label="Descrição *" rows="5" :error-messages="errors.description" class="mb-4"/>

    <div class="form-row">
      <VSelect v-model="category" label="Categoria *" :items="Object.entries(CATEGORY_LABELS).map(([value,title])=>({value,title}))"/>
      <VSelect v-if="showPriority !== false" v-model="priority" label="Prioridade" :items="Object.entries(PRIORITY_LABELS).map(([value,title])=>({value,title}))"/>
      <VTextField v-model="dueDate" label="Prazo (opcional)" type="date"/>
    </div>

    <div class="form-actions">
      <VBtn class="hub-action-button" color="primary" variant="flat" type="submit" :disabled="loading">
        <UiIcon name="check" :size="17" />
        {{ loading ? 'Salvando...' : (submitLabel || 'Salvar') }}
      </VBtn>
    </div>
  </form>
</template>

<style scoped>
.request-form { width: 100%; max-width: 760px; }
.form-intro {
  display: flex;
  align-items: center;
  gap: 11px;
  margin-bottom: 25px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--color-border);
}
.form-intro > span {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  color: var(--color-primary);
  background: var(--color-primary-light);
  border-radius: 11px;
}
.form-intro h3 { margin: 0; font-size: 0.9rem; }
.form-intro p { margin: 4px 0 0; color: var(--color-text-muted); font-size: 0.66rem; }
.form-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}
.form-actions .btn { min-width: 170px; }
@media (max-width: 760px) {
  .form-row { grid-template-columns: 1fr; }
  .form-actions .btn { width: 100%; }
}
</style>
