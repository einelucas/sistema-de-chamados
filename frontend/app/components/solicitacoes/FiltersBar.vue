<script setup lang="ts">
import { CATEGORY_LABELS, PRIORITY_LABELS, STATUS_LABELS } from '~/types/request'
import type { RequestFilters } from '~/types/request'

const props = defineProps<{ modelValue: RequestFilters }>()
const emit = defineEmits<{ 'update:modelValue': [value: RequestFilters]; change: [] }>()

function update<K extends keyof RequestFilters>(key: K, value: RequestFilters[K]) {
  emit('update:modelValue', { ...props.modelValue, [key]: value, page: 1 })
  emit('change')
}

const {isAnalystOrAdmin}=useAuth()
const {$api}=useNuxtApp()
type Context={company_id:string;company_name:string;module_slug:string;module_name:string}
const contexts=ref<Context[]>([])
const companies=computed(()=>Array.from(new Map(contexts.value.map(c=>[c.company_id,c.company_name])).entries()))
const modules=computed(()=>Array.from(new Map(contexts.value.filter(c=>!props.modelValue.company_id||c.company_id===props.modelValue.company_id).map(c=>[c.module_slug,c.module_name])).entries()))
onMounted(async()=>{if(isAnalystOrAdmin.value){try{contexts.value=await $api<Context[]>('/requests/contexts')}catch{}}})
function company(value:string){emit('update:modelValue',{...props.modelValue,company_id:value,module_slug:'',origin:value?'nexotiva':'',page:1});emit('change')}
let searchTimeout: ReturnType<typeof setTimeout>
function onSearchInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => update('search', value), 350)
}
onBeforeUnmount(()=>clearTimeout(searchTimeout))
</script>

<template>
  <div class="filters-bar card">
    <div class="search-wrap">
      <UiIcon name="search" :size="18" />
      <input
        class="search-input"
        type="search"
        placeholder="Pesquisar por título ou descrição..."
        :value="modelValue.search"
        @input="onSearchInput"
      >
    </div>

    <label v-if="isAnalystOrAdmin" class="filter-control"><span>Empresa</span><select :value="modelValue.company_id||''" @change="company(($event.target as HTMLSelectElement).value)"><option value="">Todas</option><option v-for="[id,name] in companies" :key="id" :value="id">{{name}}</option></select></label>
    <label v-if="isAnalystOrAdmin" class="filter-control"><span>Módulo</span><select :value="modelValue.module_slug||''" @change="update('module_slug',($event.target as HTMLSelectElement).value)"><option value="">Todos</option><option v-for="[id,name] in modules" :key="id" :value="id">{{name}}</option></select></label>
    <label class="filter-control">
      <span>Status</span>
      <select :value="modelValue.status" @change="update('status', ($event.target as HTMLSelectElement).value as any)">
        <option value="">Todos</option>
        <option v-for="(label, key) in STATUS_LABELS" :key="key" :value="key">{{ label }}</option>
      </select>
    </label>

    <label class="filter-control">
      <span>Prioridade</span>
      <select :value="modelValue.priority" @change="update('priority', ($event.target as HTMLSelectElement).value as any)">
        <option value="">Todas</option>
        <option v-for="(label, key) in PRIORITY_LABELS" :key="key" :value="key">{{ label }}</option>
      </select>
    </label>

    <label class="filter-control">
      <span>Categoria</span>
      <select :value="modelValue.category" @change="update('category', ($event.target as HTMLSelectElement).value as any)">
        <option value="">Todas</option>
        <option v-for="(label, key) in CATEGORY_LABELS" :key="key" :value="key">{{ label }}</option>
      </select>
    </label>

    <label class="filter-control">
      <span>Ordenação</span>
      <select
        :value="`${modelValue.sort_by}:${modelValue.sort_order}`"
        @change="
          (() => {
            const [sortBy, sortOrder] = ($event.target as HTMLSelectElement).value.split(':')
            emit('update:modelValue', { ...modelValue, sort_by: sortBy, sort_order: sortOrder as any })
            emit('change')
          })()
        "
      >
        <option value="created_at:desc">Mais recentes</option>
        <option value="created_at:asc">Mais antigas</option>
        <option value="priority:desc">Maior prioridade</option>
        <option value="status:asc">Status</option>
        <option value="due_date:asc">Prazo</option>
      </select>
    </label>
  </div>
</template>

<style scoped>
.filters-bar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
  gap: 12px;
  padding: 15px;
  margin-bottom: 16px;
}
.search-wrap {
  position: relative;
  display: flex;
  align-items: flex-end;
}
.search-wrap > svg {
  position: absolute;
  left: 14px;
  bottom: 13px;
  color: var(--placeholder);
  pointer-events: none;
}
.search-input {
  min-height: 44px;
  padding-left: 43px;
}
.search-wrap:focus-within > svg { color: var(--color-primary); }
.filter-control {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.filter-control > span {
  color: var(--color-text-muted);
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.filter-control select {
  min-height: 44px;
  padding: 10px 12px;
  color: var(--color-text-soft);
  background: var(--color-surface-soft);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  font-size: 0.75rem;
}
.filter-control select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--focus-ring);
}

@media (max-width: 1180px) {
  .filters-bar { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .search-wrap { grid-column: 1 / -1; }
}
@media (max-width: 620px) {
  .filters-bar { grid-template-columns: 1fr; }
  .search-wrap { grid-column: auto; }
}
</style>
