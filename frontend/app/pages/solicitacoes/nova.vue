<script setup lang="ts">
// Página de criação de uma nova solicitação.
definePageMeta({ middleware: 'auth' })

const { createRequest } = useRequests()
const toast = useToast()
const loading = ref(false)

async function handleSubmit(payload: any) {
  loading.value = true
  try {
    const created = await createRequest(payload)
    toast.success('Solicitação criada com sucesso.')
    await navigateTo(`/solicitacoes/${created.id}`)
  } catch (error) {
    toast.error(extractErrorMessage(error, 'Não foi possível criar a solicitação.'))
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <LayoutBreadcrumbs
      :items="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Solicitações', to: '/solicitacoes' }, { label: 'Nova' }]"
    />

    <div class="page-header">
      <div>
        <h1>Nova solicitação</h1>
        <p>Registre uma necessidade com informações claras para agilizar o atendimento.</p>
      </div>
      <VBtn to="/solicitacoes" class="hub-action-button" color="secondary" variant="outlined">
        <UiIcon name="arrowRight" :size="17" class="back-icon" /> Voltar à fila
      </VBtn>
    </div>

    <div class="form-layout">
      <section class="card form-shell">
        <SolicitacoesRequestForm submit-label="Criar solicitação" :loading="loading" @submit="handleSubmit" />
      </section>

      <aside class="card guidance-card">
        <span class="guidance-icon"><UiIcon name="activity" :size="20" /></span>
        <p class="eyebrow">Atendimento eficiente</p>
        <h2>Ajude a equipe a entender o contexto</h2>
        <p class="guidance-copy">Uma descrição objetiva reduz retrabalho e facilita a definição de prioridade.</p>
        <ul>
          <li><UiIcon name="check" :size="15" /> Use um título específico.</li>
          <li><UiIcon name="check" :size="15" /> Explique o impacto da solicitação.</li>
          <li><UiIcon name="check" :size="15" /> Informe um prazo somente quando necessário.</li>
        </ul>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.form-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(250px, 0.72fr);
  gap: 20px;
  align-items: start;
}
.form-shell { padding: clamp(20px, 3vw, 30px); }
.guidance-card {
  position: sticky;
  top: calc(var(--header-height) + 22px);
  overflow: hidden;
  padding: 24px;
}
.guidance-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 2px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
}
.guidance-icon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  margin-bottom: 20px;
  color: var(--color-primary);
  background: var(--color-primary-light);
  border: 1px solid rgba(var(--primary-rgb), 0.18);
  border-radius: 12px;
}
.eyebrow {
  margin: 0 0 7px;
  color: var(--color-accent);
  font-size: 0.61rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.guidance-card h2 { margin-bottom: 10px; font-size: 1.05rem; line-height: 1.4; }
.guidance-copy { color: var(--color-text-muted); font-size: 0.72rem; line-height: 1.7; }
.guidance-card ul { display: grid; gap: 11px; margin: 20px 0 0; padding: 18px 0 0; border-top: 1px solid var(--color-border); list-style: none; }
.guidance-card li { display: flex; align-items: flex-start; gap: 8px; color: var(--color-text-soft); font-size: 0.68rem; line-height: 1.5; }
.guidance-card li svg { flex-shrink: 0; margin-top: 2px; color: var(--color-primary); }
.back-icon { transform: rotate(180deg); }
@media (max-width: 980px) {
  .form-layout { grid-template-columns: 1fr; }
  .guidance-card { position: static; }
}
</style>
