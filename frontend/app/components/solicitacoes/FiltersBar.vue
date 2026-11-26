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
function onSearchInput(value: string | null) {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => update('search', value ?? ''), 350)
}
onBeforeUnmount(()=>clearTimeout(searchTimeout))
function sort(value:string){const [sort_by,order]=value.split(':');emit('update:modelValue',{...props.modelValue,sort_by,sort_order:order==='asc'?'asc':'desc',page:1});emit('change')}
</script>

<template>
<div class="filters-bar card">
<VTextField label="Pesquisar" placeholder="Título ou descrição" :model-value="modelValue.search||''" @update:model-value="onSearchInput" hide-details clearable class="filter-search"><template #prepend-inner><UiIcon name="search" :size="18"/></template></VTextField>
<VAutocomplete v-if="isAnalystOrAdmin" label="Empresa" :items="[{title:'Todas',value:''},...companies.map(([value,title])=>({value,title}))]" :model-value="modelValue.company_id||''" @update:model-value="company($event??'')" :menu-props="{contentClass:'hub-searchable-select-menu'}" hide-details/>
<VAutocomplete v-if="isAnalystOrAdmin" label="Módulo" :items="[{title:'Todos',value:''},...modules.map(([value,title])=>({value,title}))]" :model-value="modelValue.module_slug||''" @update:model-value="update('module_slug',$event??'')" :menu-props="{contentClass:'hub-searchable-select-menu'}" hide-details/>
<VSelect label="Status" :items="[{title:'Todos',value:''},...Object.entries(STATUS_LABELS).map(([value,title])=>({value,title}))]" :model-value="modelValue.status||''" @update:model-value="update('status',$event as RequestFilters['status'])" hide-details/>
<VSelect label="Prioridade" :items="[{title:'Todas',value:''},...Object.entries(PRIORITY_LABELS).map(([value,title])=>({value,title}))]" :model-value="modelValue.priority||''" @update:model-value="update('priority',$event as RequestFilters['priority'])" hide-details/>
<VSelect label="Categoria" :items="[{title:'Todas',value:''},...Object.entries(CATEGORY_LABELS).map(([value,title])=>({value,title}))]" :model-value="modelValue.category||''" @update:model-value="update('category',$event as RequestFilters['category'])" hide-details/>
<VSelect label="Ordenação" :items="[{title:'Mais recentes',value:'created_at:desc'},{title:'Mais antigas',value:'created_at:asc'},{title:'Maior prioridade',value:'priority:desc'},{title:'Status',value:'status:asc'},{title:'Prazo',value:'due_date:asc'}]" :model-value="`${modelValue.sort_by}:${modelValue.sort_order}`" @update:model-value="sort($event)" hide-details/>
</div></template><style scoped>.filters-bar{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));align-items:center;gap:12px;padding:16px;margin-bottom:16px}.filter-search{grid-column:span 2}@media(max-width:620px){.filters-bar{grid-template-columns:1fr}.filter-search{grid-column:auto}}</style>