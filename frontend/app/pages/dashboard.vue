<script setup lang="ts">
import { CATEGORY_LABELS, PRIORITY_LABELS, STATUS_LABELS } from '~/types/request'

definePageMeta({ middleware: 'auth' })

const { getSummary } = useDashboard()
const toast = useToast()
const themeStore = useThemeStore()

const {user}=useAuth()
const { data: summary, pending, error, refresh } = await useAsyncData('dashboard-summary:'+user.value?.id, () => getSummary())
useSilentRefresh(async()=>{if(!pending.value)await refresh()})

watch(error, (value) => {
  if (value) toast.error(extractErrorMessage(value, 'Não foi possível carregar o dashboard.'))
}, { immediate: true })

function labelFor(map: Record<string, string>, key: string) {
  return map[key] || key
}

const priorityLabels = computed(() => summary.value?.by_priority.map((item) => labelFor(PRIORITY_LABELS, item.label)) || [])
const priorityValues = computed(() => summary.value?.by_priority.map((item) => item.total) || [])
const statusLabels = computed(() => summary.value?.by_status.map((item) => labelFor(STATUS_LABELS, item.label)) || [])
const statusValues = computed(() => summary.value?.by_status.map((item) => item.total) || [])
const categoryLabels = computed(() => summary.value?.by_category.map((item) => labelFor(CATEGORY_LABELS, item.label)) || [])
const categoryValues = computed(() => summary.value?.by_category.map((item) => item.total) || [])
const periodLabels = computed(() => summary.value?.created_by_period.map((item) => item.period) || [])
const periodValues = computed(() => summary.value?.created_by_period.map((item) => item.total) || [])
const statusChartColor = computed(() => themeStore.isDark ? '#00c596' : '#2563eb')
const categoryChartColor = computed(() => themeStore.isDark ? '#66a8ff' : '#0284c7')
</script>

<template>
  <div>
    <div class="page-header dashboard-header">
      <div>
        <h1>Dashboard</h1>
        <p>Acompanhe a operação, a distribuição e a evolução das solicitações.</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary" :disabled="pending" @click="refresh()">
          <UiIcon name="activity" :size="17" />
          {{ pending ? 'Atualizando...' : 'Atualizar dados' }}
        </button>
        <NuxtLink to="/solicitacoes/nova" class="btn btn-primary">
          <UiIcon name="plus" :size="18" /> Nova solicitação
        </NuxtLink>
      </div>
    </div>

    <div v-if="pending && !summary" class="summary-grid">
      <UiSkeleton v-for="item in 5" :key="item" height="142px" />
    </div>

    <div v-else-if="error && !summary" class="card error-card">
      <span><UiIcon name="open" :size="24" /></span>
      <div>
        <h3>Não foi possível carregar os indicadores</h3>
        <p>Verifique a conexão com a API e tente novamente.</p>
      </div>
      <button class="btn btn-secondary" @click="refresh()">Tentar novamente</button>
    </div>

    <template v-else-if="summary">
      <section class="summary-grid" aria-label="Indicadores principais">
        <DashboardSummaryCard
          label="Total de solicitações"
          :value="summary.total_requests"
          icon="total"
          accent="var(--color-primary)"
          eyebrow="Volume"
        />
        <DashboardSummaryCard
          label="Abertas"
          :value="summary.open_requests"
          icon="open"
          accent="var(--color-info)"
          eyebrow="Entrada"
        />
        <DashboardSummaryCard
          label="Em andamento"
          :value="summary.in_progress_requests"
          icon="progress"
          accent="var(--color-warning)"
          eyebrow="Execução"
        />
        <DashboardSummaryCard
          label="Concluídas"
          :value="summary.completed_requests"
          icon="check"
          accent="var(--color-success)"
          eyebrow="Resultado"
        />
        <DashboardSummaryCard
          label="Atrasadas"
          :value="summary.overdue_requests"
          icon="clock"
          accent="var(--color-danger)"
          eyebrow="Atenção"
        />
      </section>

      <section class="dashboard-section">
        <div class="section-heading">
          <div>
            <span class="section-icon"><UiIcon name="activity" :size="18" /></span>
            <div><h2>Análise operacional</h2><p>Distribuição dos chamados por diferentes dimensões.</p></div>
          </div>
          <span class="section-tag">Dados consolidados</span>
        </div>

        <div class="charts-grid">
          <article class="card chart-card chart-card-wide">
            <div class="chart-heading"><div><span>Status</span><h3>Solicitações por status</h3></div><i class="accent-dot primary" /></div>
            <LazyDashboardBarChart :labels="statusLabels" :values="statusValues" :color="statusChartColor" />
          </article>
          <article class="card chart-card">
            <div class="chart-heading"><div><span>Criticidade</span><h3>Solicitações por prioridade</h3></div><i class="accent-dot accent" /></div>
            <LazyDashboardDoughnutChart :labels="priorityLabels" :values="priorityValues" />
          </article>
          <article class="card chart-card">
            <div class="chart-heading"><div><span>Origem</span><h3>Solicitações por categoria</h3></div><i class="accent-dot info" /></div>
            <LazyDashboardBarChart :labels="categoryLabels" :values="categoryValues" :color="categoryChartColor" />
          </article>
          <article class="card chart-card chart-card-wide">
            <div class="chart-heading"><div><span>Tendência</span><h3>Criadas por período</h3></div><i class="accent-dot primary" /></div>
            <LazyDashboardLineChart :labels="periodLabels" :values="periodValues" />
          </article>
        </div>
      </section>

      <section class="card recent-card">
        <div class="recent-header">
          <div class="recent-title">
            <span class="section-icon"><UiIcon name="requests" :size="18" /></span>
            <div><h2>Solicitações recentes</h2><p>Últimos registros adicionados à central.</p></div>
          </div>
          <div class="recent-meta">
            <span v-if="summary.average_completion_hours !== null" class="avg-time">
              <UiIcon name="clock" :size="15" /> Média de conclusão: <strong>{{ summary.average_completion_hours }}h</strong>
            </span>
            <NuxtLink to="/solicitacoes" class="view-all">Ver todas <UiIcon name="arrowRight" :size="15" /></NuxtLink>
          </div>
        </div>

        <UiEmptyState
          v-if="summary.recent_requests.length === 0"
          icon="requests"
          title="Nenhuma solicitação recente"
          description="Assim que novas solicitações forem criadas, elas aparecerão aqui."
        />
        <div v-else class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Título</th>
                <th>Status</th>
                <th>Prioridade</th>
                <th>Solicitante</th>
                <th>Criada em</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in summary.recent_requests" :key="item.id" class="row-link" @click="navigateTo(`/solicitacoes/${item.id}`)">
                <td class="title-cell"><span class="request-id">#{{ item.id }}</span><strong>{{ item.title }}</strong></td>
                <td><UiStatusBadge :status="item.status" /></td>
                <td><UiPriorityBadge :priority="item.priority" /></td>
                <td>{{ item.requester.name }}</td>
                <td>{{ formatDate(item.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.dashboard-header { align-items: center; }
.header-actions { display: flex; flex-wrap: wrap; gap: 10px; }
.summary-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 15px;
  margin-bottom: 32px;
}
.error-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
}
.error-card > span {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  color: var(--color-danger);
  background: var(--color-danger-light);
  border-radius: 13px;
}
.error-card div { flex: 1; }
.error-card h3 { margin: 0 0 5px; }
.error-card p { margin: 0; color: var(--color-text-muted); font-size: 0.78rem; }
.dashboard-section { margin-bottom: 24px; }
.section-heading,
.recent-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 15px;
}
.section-heading > div,
.recent-title {
  display: flex;
  align-items: center;
  gap: 12px;
}
.section-icon {
  width: 39px;
  height: 39px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  color: var(--color-primary);
  background: var(--color-primary-light);
  border: 1px solid var(--color-primary-border);
  border-radius: 11px;
}
.section-heading h2,
.recent-title h2 { margin: 0; font-size: 0.96rem; }
.section-heading p,
.recent-title p { margin: 4px 0 0; color: var(--color-text-muted); font-size: 0.68rem; }
.section-tag {
  padding: 6px 10px;
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  font-size: 0.62rem;
}
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 15px;
}
.chart-card { min-width: 0; padding: 20px; overflow: hidden; }
.chart-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.chart-heading span {
  color: var(--color-text-muted);
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.11em;
  text-transform: uppercase;
}
.chart-heading h3 { margin: 5px 0 0; font-size: 0.87rem; }
.accent-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  box-shadow: 0 0 12px currentColor;
}
.accent-dot.primary { color: var(--color-primary); background: var(--color-primary); }
.accent-dot.accent { color: var(--color-accent); background: var(--color-accent); }
.accent-dot.info { color: var(--color-info); background: var(--color-info); }
.recent-card { padding: 20px 0 0; overflow: hidden; }
.recent-header { padding: 0 20px 17px; margin-bottom: 0; border-bottom: 1px solid var(--color-border); }
.recent-meta { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.avg-time,
.view-all {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-muted);
  font-size: 0.66rem;
}
.avg-time strong { color: var(--color-text-soft); }
.view-all { color: var(--color-primary); font-weight: 700; text-decoration: none; }
.title-cell { min-width: 240px; }
.title-cell strong { color: var(--color-text-soft); font-size: 0.79rem; }
.request-id { display: block; margin-bottom: 4px; color: var(--color-primary); font-size: 0.61rem; font-weight: 700; }
.row-link { cursor: pointer; }

@media (max-width: 1280px) {
  .summary-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 800px) {
  .summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .charts-grid { grid-template-columns: 1fr; }
  .section-heading,
  .recent-header { align-items: flex-start; flex-direction: column; }
}
@media (max-width: 540px) {
  .summary-grid { grid-template-columns: 1fr; }
  .header-actions { width: 100%; }
  .header-actions .btn { flex: 1; }
  .error-card { align-items: flex-start; flex-wrap: wrap; }
}
</style>
