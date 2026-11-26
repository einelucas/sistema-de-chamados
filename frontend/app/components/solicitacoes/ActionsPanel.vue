<script setup lang="ts">
import { PRIORITY_LABELS, STATUS_LABELS } from '~/types/request'
import type { RequestItem, RequestPriority, RequestStatus } from '~/types/request'
import type { User } from '~/types/user'

const props = defineProps<{ request: RequestItem; assignableUsers: User[] }>()
const emit = defineEmits<{
  'change-status': [status: RequestStatus]
  'change-priority': [priority: RequestPriority]
  'change-assignee': [assigneeId: number | null]
}>()

const { isAnalystOrAdmin } = useAuth()

</script>

<template>
  <div class="actions-panel card">
    <div class="panel-heading">
      <span><UiIcon name="activity" :size="18" /></span>
      <div><h3>Gerenciar solicitação</h3><p>Atualize o andamento e a responsabilidade.</p></div>
    </div>

    <VSelect label="Status" :items="Object.entries(STATUS_LABELS).map(([value,title])=>({value,title}))" :model-value="request.status" :disabled="!isAnalystOrAdmin" @update:model-value="emit('change-status',$event as RequestStatus)" class="mb-4"/>

    <VSelect label="Prioridade" :items="Object.entries(PRIORITY_LABELS).map(([value,title])=>({value,title}))" :model-value="request.priority" :disabled="!isAnalystOrAdmin" @update:model-value="emit('change-priority',$event as RequestPriority)" class="mb-4"/>

    <VAutocomplete label="Responsável" :items="[{title:'Não atribuído',value:0},...assignableUsers.map(u=>({title:u.name,value:u.id}))]" :model-value="request.assignee?.id??0" :disabled="!isAnalystOrAdmin" @update:model-value="emit('change-assignee',$event||null)" :menu-props="{contentClass:'hub-searchable-select-menu'}" class="mb-4"/>

    <p v-if="!isAnalystOrAdmin" class="hint">
      <UiIcon name="shield" :size="15" /> Apenas analistas e administradores podem alterar estes campos.
    </p>
  </div>
</template>

<style scoped>
.actions-panel { padding: 20px; overflow: hidden; }
.actions-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
}
.panel-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--color-border);
}
.panel-heading > span {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  color: var(--color-primary);
  background: var(--color-primary-light);
  border-radius: 10px;
}
.panel-heading h3 { margin: 0; font-size: 0.87rem; }
.panel-heading p { margin: 3px 0 0; color: var(--color-text-muted); font-size: 0.61rem; line-height: 1.4; }
.hint {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  margin: 4px 0 0;
  padding: 10px;
  color: var(--color-text-muted);
  background: var(--surface-translucent);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  font-size: 0.64rem;
  line-height: 1.45;
}
</style>
