<script setup lang="ts">
// Listagem de solicitações com filtros, pesquisa, ordenação e paginação.
import type { RequestFilters, RequestListItem } from '~/types/request'

definePageMeta({ middleware: 'auth' })

const { listRequests } = useRequests()
const toast = useToast()

const filters = ref<RequestFilters>({
  page: 1,
  page_size: 10,
  search: '',
  status: '',
  priority: '',
  category: '',
  sort_by: 'created_at',
  sort_order: 'desc',
})

const items = ref<RequestListItem[]>([])
const total = ref(0)
const totalPages = ref(1)
const loading = ref(true)
const refreshing=ref(false), error=ref(''), lastUpdated=ref(0)
const {user}=useAuth()
let sequence=0, disposed=false

async function load(quiet=false) {
  const current=++sequence
  if(!quiet)loading.value=true;else refreshing.value=true
  error.value=''
  try {
    const response = await listRequests(filters.value)
    if(disposed||current!==sequence)return
    items.value = response.items
    lastUpdated.value=Date.now()
    total.value = response.total
    totalPages.value = response.total_pages
  } catch (error) {
    if(!disposed&&current===sequence){if([401,403].includes((error as any)?.statusCode)){items.value=[];total.value=0};if(!quiet)toast.error(extractErrorMessage(error,'Não foi possível carregar as solicitações.'))}
  } finally {
    if(current===sequence){loading.value=false;refreshing.value=false}
  }
}

onMounted(()=>{
  try{const saved=JSON.parse(localStorage.getItem('central:filters:'+user.value?.id)||'null');if(saved&&typeof saved==='object')filters.value={...filters.value,status:saved.status||'',priority:saved.priority||'',category:saved.category||'',company_id:typeof saved.company_id==='string'?saved.company_id:'',module_slug:typeof saved.module_slug==='string'?saved.module_slug:'',page:1}}catch{}
  void load()
})
watch(filters,value=>{if(user.value)try{const {status,priority,category,company_id,module_slug}=value;localStorage.setItem('central:filters:'+user.value.id,JSON.stringify({status,priority,category,company_id,module_slug}))}catch{}},{deep:true})
useSilentRefresh(async()=>{if(!loading.value&&!refreshing.value)await load(true)})
onBeforeUnmount(()=>{disposed=true;sequence++})

function changePage(page: number) {
  filters.value = { ...filters.value, page }
  load()
}
</script>

<template>
  <div>
    <LayoutBreadcrumbs :items="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Solicitações' }]" />

    <div class="page-header">
      <div>
        <h1>Solicitações</h1>
        <p>Acompanhe e gerencie as solicitações internas</p>
      </div>
      <NuxtLink to="/solicitacoes/nova" class="btn btn-primary"><UiIcon name="plus" :size="18" /> Nova solicitação</NuxtLink>
    </div>

    <SolicitacoesFiltersBar v-model="filters" @change="load()" />

    <div class="card requests-card">
      <div class="list-heading">
        <div><span><UiIcon name="requests" :size="18" /></span><div><h2>Fila de solicitações</h2><p>{{ total }} registro(s) encontrado(s)</p></div></div>
        <span class="live-dot" role="status"><i /> {{ refreshing ? "Atualizando..." : lastUpdated ? "Atualizado às "+new Date(lastUpdated).toLocaleTimeString("pt-BR") : "Aguardando atualização" }}</span>
      </div>
      <div v-if="loading" style="padding: 20px; display: flex; flex-direction: column; gap: 10px">
        <UiSkeleton v-for="i in 5" :key="i" height="40px" />
      </div>
      <UiEmptyState
        v-else-if="items.length === 0"
        icon="search"
        title="Nenhuma solicitação encontrada"
        description="Ajuste os filtros ou crie uma nova solicitação."
      />
      <SolicitacoesRequestsTable v-else :items="items" />
    </div>

    <SolicitacoesPagination :page="filters.page || 1" :total-pages="totalPages" :total="total" @update:page="changePage" />
  </div>
</template>

<style scoped>
.requests-card { overflow: hidden; }
.list-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 16px 18px;
  border-bottom: 1px solid var(--color-border);
}
.list-heading > div {
  display: flex;
  align-items: center;
  gap: 11px;
}
.list-heading > div > span {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  color: var(--color-primary);
  background: var(--color-primary-light);
  border-radius: 10px;
}
.list-heading h2 { margin: 0; font-size: 0.9rem; }
.list-heading p { margin: 3px 0 0; color: var(--color-text-muted); font-size: 0.62rem; }
.live-dot {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-muted);
  font-size: 0.61rem;
}
.live-dot i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-primary);
  box-shadow: 0 0 8px var(--color-primary);
}
@media (max-width: 540px) {
  .list-heading { align-items: flex-start; }
  .live-dot { display: none; }
}
</style>
