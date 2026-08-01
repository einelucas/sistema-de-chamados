<script setup lang="ts">
import type { RequestStatus } from '~/types/request'
import { STATUS_LABELS } from '~/types/request'

defineProps<{ status: RequestStatus }>()

const classMap: Record<RequestStatus, string> = {
  ABERTA: 'badge-status-aberta',
  EM_ANDAMENTO: 'badge-status-em-andamento',
  AGUARDANDO: 'badge-status-aguardando',
  CONCLUIDA: 'badge-status-concluida',
  CANCELADA: 'badge-status-cancelada',
}
</script>

<template>
  <span class="badge" :class="classMap[status]">{{ STATUS_LABELS[status] }}</span>
</template>
