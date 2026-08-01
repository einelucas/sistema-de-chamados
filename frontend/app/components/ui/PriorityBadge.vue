<script setup lang="ts">
import type { RequestPriority } from '~/types/request'
import { PRIORITY_LABELS } from '~/types/request'

defineProps<{ priority: RequestPriority }>()

const classMap: Record<RequestPriority, string> = {
  BAIXA: 'badge-priority-baixa',
  MEDIA: 'badge-priority-media',
  ALTA: 'badge-priority-alta',
  CRITICA: 'badge-priority-critica',
}
</script>

<template>
  <span class="badge" :class="classMap[priority]">{{ PRIORITY_LABELS[priority] }}</span>
</template>
