<script setup lang="ts">
// Página de edição de uma solicitação existente.
definePageMeta({ middleware: 'auth' })

const route = useRoute()
const requestId = Number(route.params.id)

const { getRequest, updateRequest } = useRequests()
const toast = useToast()

const request = ref<Awaited<ReturnType<typeof getRequest>> | null>(null)
const loading = ref(true)
const saving = ref(false)

onMounted(async () => {
  try {
    request.value = await getRequest(requestId)
  } catch (error) {
    toast.error(extractErrorMessage(error, 'Não foi possível carregar a solicitação.'))
  } finally {
    loading.value = false
  }
})

async function handleSubmit(payload: any) {
  saving.value = true
  try {
    const { priority, ...updatePayload } = payload
    await updateRequest(requestId, {...updatePayload,expected_version:request.value?.version})
    toast.success('Solicitação atualizada com sucesso.')
    await navigateTo(`/solicitacoes/${requestId}`)
  } catch (error) {
    toast.error(extractErrorMessage(error, 'Não foi possível atualizar a solicitação.'))
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <LayoutBreadcrumbs
      :items="[
        { label: 'Dashboard', to: '/dashboard' },
        { label: 'Solicitações', to: '/solicitacoes' },
        { label: request ? `#${request.id}` : '...', to: request ? `/solicitacoes/${request.id}` : undefined },
        { label: 'Editar' },
      ]"
    />

    <div class="page-header">
      <div>
        <h1>Editar solicitação</h1>
        <p>Atualize as informações de contexto sem alterar o histórico do atendimento.</p>
      </div>
      <VBtn :to="`/solicitacoes/${requestId}`" class="hub-action-button" color="secondary" variant="outlined">
        <UiIcon name="arrowRight" :size="17" class="back-icon" /> Voltar aos detalhes
      </VBtn>
    </div>

    <div v-if="loading" class="card loading-card">
      <UiSkeleton height="36px" width="42%" />
      <UiSkeleton height="52px" />
      <UiSkeleton height="150px" />
      <UiSkeleton height="52px" />
    </div>

    <section v-else-if="request" class="card form-shell">
      <div class="edit-context">
        <span><UiIcon name="edit" :size="18" /></span>
        <div>
          <strong>Solicitação #{{ request.id }}</strong>
          <p>As alterações ficarão registradas no histórico.</p>
        </div>
      </div>
      <SolicitacoesRequestForm
        :initial-title="request.title"
        :initial-description="request.description"
        :initial-category="request.category"
        :initial-due-date="request.due_date"
        :show-priority="false"
        submit-label="Salvar alterações"
        :loading="saving"
        @submit="handleSubmit"
      />
    </section>
  </div>
</template>

<style scoped>
.form-shell { max-width: 900px; padding: clamp(20px, 3vw, 30px); }
.loading-card { display: grid; gap: 14px; max-width: 900px; padding: 28px; }
.edit-context {
  display: flex;
  align-items: center;
  gap: 11px;
  margin: -4px 0 24px;
  padding: 12px 14px;
  color: var(--color-text-soft);
  background: rgba(var(--accent-rgb), 0.055);
  border: 1px solid rgba(var(--accent-rgb), 0.18);
  border-radius: 12px;
}
.edit-context > span { width: 34px; height: 34px; display: grid; place-items: center; flex-shrink: 0; color: var(--color-accent); background: var(--color-accent-light); border-radius: 9px; }
.edit-context strong { font-size: 0.72rem; }
.edit-context p { margin: 3px 0 0; color: var(--color-text-muted); font-size: 0.62rem; }
.back-icon { transform: rotate(180deg); }
</style>
