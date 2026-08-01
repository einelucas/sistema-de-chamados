<script setup lang="ts">
// Página de detalhes de uma solicitação: dados, ações rápidas, comentários, histórico e anexos.
import type { RequestItem, RequestPriority, RequestStatus } from '~/types/request'
import { CATEGORY_LABELS } from '~/types/request'
import type { User } from '~/types/user'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const requestId = Number(route.params.id)

const { getRequest, deleteRequest, changeStatus, changePriority, changeAssignee } = useRequests()
const { listUsers } = useUsers()
const { user, isAnalystOrAdmin, isAdmin } = useAuth()
const toast = useToast()

const request = ref<RequestItem | null>(null)
const loading = ref(true)
const assignableUsers = ref<User[]>([])
const deleteDialogOpen = ref(false)
const deleting = ref(false)

async function load() {
  loading.value = true
  try {
    request.value = await getRequest(requestId)
  } catch (error) {
    toast.error(extractErrorMessage(error, 'Não foi possível carregar a solicitação.'))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await load()
  if (isAnalystOrAdmin.value) {
    try {
      const response = await listUsers(1, 100)
      assignableUsers.value = response.items.filter((u) => u.is_active)
    } catch {
      // Silenciosamente ignora: o painel de ações apenas não terá a lista de responsáveis.
    }
  }
})

const canEdit = computed(() => {
  if (!request.value || !user.value) return false
  if (isAdmin.value) return true
  return request.value.requester.id === user.value.id && request.value.status === 'ABERTA'
})

const canDelete = computed(() => {
  if (!request.value || !user.value) return false
  return isAdmin.value || request.value.requester.id === user.value.id
})

async function handleStatusChange(status: RequestStatus) {
  if (!request.value) return
  try {
    request.value = await changeStatus(request.value.id, status)
    toast.success('Status atualizado.')
  } catch (error) {
    toast.error(extractErrorMessage(error))
    await load()
  }
}

async function handlePriorityChange(priority: RequestPriority) {
  if (!request.value) return
  try {
    request.value = await changePriority(request.value.id, priority)
    toast.success('Prioridade atualizada.')
  } catch (error) {
    toast.error(extractErrorMessage(error))
    await load()
  }
}

async function handleAssigneeChange(assigneeId: number | null) {
  if (!request.value) return
  try {
    request.value = await changeAssignee(request.value.id, assigneeId)
    toast.success('Responsável atualizado.')
  } catch (error) {
    toast.error(extractErrorMessage(error))
    await load()
  }
}

async function confirmDelete() {
  if (!request.value) return
  deleting.value = true
  try {
    await deleteRequest(request.value.id)
    toast.success('Solicitação removida.')
    await navigateTo('/solicitacoes')
  } catch (error) {
    toast.error(extractErrorMessage(error))
  } finally {
    deleting.value = false
    deleteDialogOpen.value = false
  }
}
</script>

<template>
  <div>
    <LayoutBreadcrumbs
      :items="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Solicitações', to: '/solicitacoes' }, { label: request ? `#${request.id}` : '...' }]"
    />

    <div v-if="loading" class="detail-loading">
      <UiSkeleton height="34px" width="44%" />
      <UiSkeleton height="24px" width="28%" />
      <div class="loading-grid">
        <UiSkeleton height="300px" />
        <UiSkeleton height="300px" />
      </div>
    </div>

    <template v-else-if="request">
      <div class="detail-header">
        <div class="detail-title">
          <p class="request-kicker"><UiIcon name="requests" :size="14" /> Solicitação #{{ request.id }}</p>
          <h1>{{ request.title }}</h1>
          <div class="badges-row">
            <UiStatusBadge :status="request.status" />
            <UiPriorityBadge :priority="request.priority" />
            <span class="category-tag">{{ CATEGORY_LABELS[request.category] }}</span>
          </div>
        </div>
        <div class="detail-actions">
          <NuxtLink v-if="canEdit" :to="`/solicitacoes/${request.id}/editar`" class="btn btn-secondary">
            <UiIcon name="edit" :size="16" /> Editar
          </NuxtLink>
          <button v-if="canDelete" class="btn btn-danger" @click="deleteDialogOpen = true">
            <UiIcon name="trash" :size="16" /> Excluir
          </button>
        </div>
      </div>

      <div class="detail-grid">
        <main class="detail-main">
          <section class="card info-card">
            <div class="section-heading">
              <span><UiIcon name="requests" :size="18" /></span>
              <div><h2>Visão geral</h2><p>Contexto e informações principais do atendimento.</p></div>
            </div>

            <div class="description-block">
              <span class="meta-label">Descrição</span>
              <p class="description">{{ request.description }}</p>
            </div>

            <div class="meta-grid">
              <div class="meta-item">
                <span class="meta-icon"><UiIcon name="user" :size="17" /></span>
                <div><span class="meta-label">Solicitante</span><p>{{ request.requester.name }}</p></div>
              </div>
              <div class="meta-item">
                <span class="meta-icon"><UiIcon name="users" :size="17" /></span>
                <div><span class="meta-label">Responsável</span><p>{{ request.assignee?.name || 'Não atribuído' }}</p></div>
              </div>
              <div class="meta-item">
                <span class="meta-icon"><UiIcon name="clock" :size="17" /></span>
                <div><span class="meta-label">Criada em</span><p>{{ formatDate(request.created_at) }}</p></div>
              </div>
              <div class="meta-item">
                <span class="meta-icon"><UiIcon name="activity" :size="17" /></span>
                <div>
                  <span class="meta-label">Prazo</span>
                  <p :class="{ overdue: isOverdue(request.due_date, request.status) }">
                    {{ request.due_date ? formatDate(request.due_date) : 'Sem prazo definido' }}
                  </p>
                </div>
              </div>
              <div v-if="request.completed_at" class="meta-item">
                <span class="meta-icon"><UiIcon name="check" :size="17" /></span>
                <div><span class="meta-label">Concluída em</span><p>{{ formatDate(request.completed_at) }}</p></div>
              </div>
            </div>
          </section>

          <section class="card content-card">
            <SolicitacoesCommentsSection :request-id="request.id" />
          </section>

          <section class="card content-card">
            <SolicitacoesAttachmentsSection :request-id="request.id" />
          </section>
        </main>

        <aside class="detail-side">
          <SolicitacoesActionsPanel
            :request="request"
            :assignable-users="assignableUsers"
            @change-status="handleStatusChange"
            @change-priority="handlePriorityChange"
            @change-assignee="handleAssigneeChange"
          />
          <section class="card history-card">
            <SolicitacoesHistoryTimeline :request-id="request.id" />
          </section>
        </aside>
      </div>
    </template>

    <UiConfirmDialog
      v-model="deleteDialogOpen"
      title="Excluir solicitação"
      message="Tem certeza de que deseja excluir esta solicitação? Esta ação pode ser revertida apenas por um administrador."
      confirm-label="Excluir"
      danger
      :loading="deleting"
      @confirm="confirmDelete"
    />
  </div>
</template>

<style scoped>
.detail-loading { display: grid; gap: 12px; }
.loading-grid { display: grid; grid-template-columns: minmax(0, 1.65fr) minmax(280px, 0.72fr); gap: 20px; margin-top: 8px; }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 18px; margin-bottom: 24px; }
.detail-title { position: relative; padding-left: 18px; }
.detail-title::before { content: ''; position: absolute; inset: 3px auto 2px 0; width: 3px; border-radius: 99px; background: linear-gradient(180deg, var(--color-primary), var(--color-accent)); box-shadow: 0 0 18px var(--color-primary-glow); }
.request-kicker { display: flex; align-items: center; gap: 6px; margin: 0 0 6px; color: var(--color-primary); font-size: 0.62rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
.detail-title h1 { max-width: 820px; margin-bottom: 0; line-height: 1.25; }
.badges-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.category-tag { display: inline-flex; align-items: center; min-height: 25px; padding: 4px 10px; color: var(--color-text-soft); background: var(--table-row-hover); border: 1px solid var(--color-border); border-radius: var(--radius-full); font-size: 0.62rem; font-weight: 700; }
.detail-actions { display: flex; flex-wrap: wrap; gap: 9px; }
.detail-grid { display: grid; grid-template-columns: minmax(0, 1.65fr) minmax(280px, 0.72fr); gap: 20px; align-items: start; }
.detail-main, .detail-side { display: flex; flex-direction: column; gap: 20px; min-width: 0; }
.detail-side { position: sticky; top: calc(var(--header-height) + 20px); }
.info-card, .content-card, .history-card { padding: clamp(18px, 2.6vw, 24px); overflow: hidden; }
.info-card::before { content: ''; position: absolute; inset: 0 auto 0 0; width: 3px; background: linear-gradient(180deg, var(--color-primary), transparent 70%); }
.section-heading { display: flex; align-items: center; gap: 11px; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--color-border); }
.section-heading > span { width: 38px; height: 38px; display: grid; place-items: center; flex-shrink: 0; color: var(--color-primary); background: var(--color-primary-light); border-radius: 10px; }
.section-heading h2 { margin: 0; font-size: 0.92rem; }
.section-heading p { margin: 3px 0 0; color: var(--color-text-muted); font-size: 0.63rem; }
.description-block { padding: 16px; background: var(--surface-translucent); border: 1px solid var(--color-border); border-radius: 13px; }
.description { margin: 7px 0 0; color: var(--color-text-soft); font-size: 0.78rem; line-height: 1.75; white-space: pre-wrap; }
.meta-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 14px; }
.meta-item { display: flex; align-items: center; gap: 10px; min-width: 0; padding: 12px; background: var(--surface-translucent); border: 1px solid var(--color-border); border-radius: 12px; }
.meta-icon { width: 33px; height: 33px; display: grid; place-items: center; flex-shrink: 0; color: var(--color-primary); background: var(--color-primary-light); border-radius: 9px; }
.meta-label { color: var(--color-text-muted); font-size: 0.56rem; font-weight: 700; letter-spacing: 0.075em; text-transform: uppercase; }
.meta-item p { overflow: hidden; margin: 3px 0 0; color: var(--color-text-soft); font-size: 0.7rem; font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
.overdue { color: var(--color-danger) !important; }
@media (max-width: 1040px) {
  .detail-grid, .loading-grid { grid-template-columns: 1fr; }
  .detail-side { position: static; }
}
@media (max-width: 620px) {
  .detail-header, .detail-actions { width: 100%; }
  .detail-actions .btn { flex: 1; }
  .meta-grid { grid-template-columns: 1fr; }
}
</style>
