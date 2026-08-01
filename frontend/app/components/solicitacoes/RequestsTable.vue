<script setup lang="ts">
import type { RequestListItem } from '~/types/request'
import { CATEGORY_LABELS } from '~/types/request'

defineProps<{ items: RequestListItem[] }>()
</script>

<template>
  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          <th>Solicitação</th>
          <th>Categoria</th>
          <th>Prioridade</th>
          <th>Status</th>
          <th>Solicitante</th>
          <th>Responsável</th>
          <th>Prazo</th>
          <th>Criada em</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id" class="row-link" @click="navigateTo(`/solicitacoes/${item.id}`)">
          <td class="title-cell">
            <span>#{{ item.id }}</span>
            <strong>{{ item.title }}</strong>
          </td>
          <td><span class="category-pill">{{ CATEGORY_LABELS[item.category] }}</span></td>
          <td><UiPriorityBadge :priority="item.priority" /></td>
          <td><UiStatusBadge :status="item.status" /></td>
          <td>{{ item.requester.name }}</td>
          <td>{{ item.assignee?.name || '—' }}</td>
          <td :class="{ overdue: isOverdue(item.due_date, item.status) }">
            {{ item.due_date ? formatDateOnly(item.due_date) : '—' }}
          </td>
          <td>{{ formatDateOnly(item.created_at) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.row-link { cursor: pointer; }
.title-cell { min-width: 245px; max-width: 330px; }
.title-cell span {
  display: block;
  margin-bottom: 4px;
  color: var(--color-primary);
  font-size: 0.59rem;
  font-weight: 700;
}
.title-cell strong {
  display: block;
  overflow: hidden;
  color: var(--color-text-soft);
  font-size: 0.77rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.category-pill {
  display: inline-flex;
  padding: 5px 9px;
  color: var(--color-text-muted);
  background: var(--table-row-hover);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  font-size: 0.65rem;
  font-weight: 600;
}
.overdue { color: var(--color-danger); font-weight: 700; }
</style>
