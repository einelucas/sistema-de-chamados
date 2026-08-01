<script setup lang="ts">
import type { UserRole } from '~/types/user'

defineProps<{ role: UserRole }>()

const labels: Record<UserRole, string> = { ADMIN: 'Administrador', ANALYST: 'Analista', USER: 'Usuário' }
const classes: Record<UserRole, string> = { ADMIN: 'role-admin', ANALYST: 'role-analyst', USER: 'role-user' }
</script>

<template>
  <span class="badge role-badge" :class="classes[role]">{{ labels[role] }}</span>
</template>

<style scoped>
.role-admin { color: var(--color-danger); background: var(--color-danger-light); }
.role-analyst { color: var(--color-info); background: var(--color-info-light); }
.role-user { color: var(--color-text-muted); background: rgba(100, 116, 139, 0.10); }
</style>
