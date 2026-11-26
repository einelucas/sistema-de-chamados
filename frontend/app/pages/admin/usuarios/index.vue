<script setup lang="ts">
// Listagem de usuários (área administrativa): listar, ativar/desativar, ver detalhes.
import type { User } from '~/types/user'

definePageMeta({ middleware: 'admin' })

const { listUsers, activateUser, deactivateUser } = useUsers()
const toast = useToast()

const users = ref<User[]>([])
const loading = ref(true)
const page = ref(1)
const totalPages = ref(1)
const total = ref(0)
const togglingId = ref<number | null>(null)

async function load() {
  loading.value = true
  try {
    const response = await listUsers(page.value, 20)
    users.value = response.items
    totalPages.value = response.total_pages
    total.value = response.total
  } catch (error) {
    toast.error(extractErrorMessage(error, 'Não foi possível carregar os usuários.'))
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function toggleActive(user: User) {
  togglingId.value = user.id
  try {
    const updated = user.is_active ? await deactivateUser(user.id) : await activateUser(user.id)
    const index = users.value.findIndex((u) => u.id === user.id)
    if (index !== -1) users.value[index] = updated
    toast.success(updated.is_active ? 'Usuário ativado.' : 'Usuário desativado.')
  } catch (error) {
    toast.error(extractErrorMessage(error))
  } finally {
    togglingId.value = null
  }
}
</script>

<template>
  <div>
    <LayoutBreadcrumbs :items="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Usuários' }]" />

    <div class="page-header">
      <div>
        <h1>Usuários</h1>
        <p>Gerencie os usuários do sistema</p>
      </div>
      <VBtn to="/admin/usuarios/novo" class="hub-action-button" color="primary" variant="flat"><UiIcon name="plus" :size="18" /> Novo usuário</VBtn>
    </div>

    <div class="card users-card">
      <div class="list-heading">
        <div><span><UiIcon name="users" :size="18" /></span><div><h2>Usuários cadastrados</h2><p>{{ total }} registro(s) no sistema</p></div></div>
        <span class="admin-chip"><UiIcon name="shield" :size="14" /> Área administrativa</span>
      </div>
      <div v-if="loading" style="padding: 20px; display: flex; flex-direction: column; gap: 10px">
        <UiSkeleton v-for="i in 5" :key="i" height="40px" />
      </div>
      <UiEmptyState v-else-if="users.length === 0" icon="users" title="Nenhum usuário encontrado" />
      <div v-else class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>E-mail</th>
              <th>Papel</th>
              <th>Status</th>
              <th>Criado em</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>
                <NuxtLink :to="`/admin/usuarios/${user.id}`" class="user-link">{{ user.name }}</NuxtLink>
              </td>
              <td>{{ user.email }}</td>
              <td><UiRoleBadge :role="user.role" /></td>
              <td>
                <span class="badge" :style="{ background: user.is_active ? 'var(--color-success-light)' : 'var(--color-danger-light)', color: user.is_active ? 'var(--color-success)' : 'var(--color-danger)' }">
                  {{ user.is_active ? 'Ativo' : 'Inativo' }}
                </span>
              </td>
              <td>{{ formatDateOnly(user.created_at) }}</td>
              <td>
                <VBtn class="hub-action-button" color="secondary" variant="text" :disabled="togglingId === user.id" @click="toggleActive(user)" type="button">
                  <UiIcon :name="user.is_active ? 'close' : 'check'" :size="14" /> {{ togglingId === user.id ? 'Aguarde...' : user.is_active ? 'Desativar' : 'Ativar' }}
                </VBtn>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <SolicitacoesPagination
      :page="page"
      :total-pages="totalPages"
      :total="total"
      @update:page="(p) => { page = p; load() }"
    />
  </div>
</template>

<style scoped>
.users-card { overflow: hidden; }
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
.admin-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 9px;
  color: var(--color-accent);
  background: var(--color-accent-light);
  border: 1px solid rgba(var(--accent-rgb), 0.22);
  border-radius: var(--radius-full);
  font-size: 0.61rem;
  font-weight: 700;
}
.user-link { color: var(--color-text-soft); font-weight: 700; text-decoration: none; }
.user-link:hover { color: var(--color-primary); }
@media (max-width: 600px) { .admin-chip { display: none; } }
</style>
