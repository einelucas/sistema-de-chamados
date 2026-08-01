<script setup lang="ts">
// Página de detalhes/edição de um usuário: atualizar dados, papel, status e redefinir senha.
definePageMeta({ middleware: 'admin' })

const route = useRoute()
const userId = Number(route.params.id)

const { getUser, updateUser, resetPassword, deleteUser } = useUsers()
const toast = useToast()

const user = ref<Awaited<ReturnType<typeof getUser>> | null>(null)
const loading = ref(true)
const saving = ref(false)

const name = ref('')
const email = ref('')
const role = ref<'ADMIN' | 'ANALYST' | 'USER'>('USER')
const newPassword = ref('')
const resettingPassword = ref(false)
const deleteDialogOpen = ref(false)
const deleting = ref(false)

onMounted(async () => {
  try {
    user.value = await getUser(userId)
    name.value = user.value.name
    email.value = user.value.email
    role.value = user.value.role
  } catch (error) {
    toast.error(extractErrorMessage(error, 'Não foi possível carregar o usuário.'))
  } finally {
    loading.value = false
  }
})

async function saveChanges() {
  saving.value = true
  try {
    user.value = await updateUser(userId, { name: name.value.trim(), email: email.value.trim(), role: role.value })
    toast.success('Usuário atualizado.')
  } catch (error) {
    toast.error(extractErrorMessage(error))
  } finally {
    saving.value = false
  }
}

async function handleResetPassword() {
  if (newPassword.value.length < 6) {
    toast.error('A nova senha deve ter ao menos 6 caracteres.')
    return
  }
  resettingPassword.value = true
  try {
    await resetPassword(userId, newPassword.value)
    newPassword.value = ''
    toast.success('Senha redefinida com sucesso.')
  } catch (error) {
    toast.error(extractErrorMessage(error))
  } finally {
    resettingPassword.value = false
  }
}

async function confirmDelete() {
  deleting.value = true
  try {
    await deleteUser(userId)
    toast.success('Usuário removido.')
    await navigateTo('/admin/usuarios')
  } catch (error) {
    toast.error(extractErrorMessage(error))
  } finally {
    deleting.value = false
    deleteDialogOpen.value = false
  }
}
</script>

<template>
  <div>
    <LayoutBreadcrumbs
      :items="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Usuários', to: '/admin/usuarios' }, { label: user ? user.name : '...' }]"
    />

    <div v-if="loading" class="loading-layout">
      <UiSkeleton height="90px" />
      <div class="loading-grid"><UiSkeleton height="330px" /><UiSkeleton height="330px" /></div>
    </div>

    <template v-else-if="user">
      <div class="user-hero card">
        <div class="identity-group">
          <span class="avatar-xl">{{ user.name.charAt(0).toUpperCase() }}</span>
          <div>
            <p class="user-kicker"><UiIcon name="shield" :size="14" /> Área administrativa</p>
            <h1>{{ user.name }}</h1>
            <p class="user-email">{{ user.email }}</p>
            <div class="user-badges">
              <UiRoleBadge :role="user.role" />
              <span class="badge" :class="user.is_active ? 'active-badge' : 'inactive-badge'">{{ user.is_active ? 'Ativo' : 'Inativo' }}</span>
            </div>
          </div>
        </div>
        <NuxtLink to="/admin/usuarios" class="btn btn-secondary"><UiIcon name="arrowRight" :size="17" class="back-icon" /> Voltar</NuxtLink>
      </div>

      <div class="cards-grid">
        <section class="card form-card">
          <div class="card-heading">
            <span><UiIcon name="edit" :size="18" /></span>
            <div><h2>Dados do usuário</h2><p>Atualize identidade e nível de acesso.</p></div>
          </div>
          <div class="form-field">
            <label for="user-name">Nome</label>
            <input id="user-name" v-model="name" type="text" autocomplete="name" />
          </div>
          <div class="form-field">
            <label for="user-email">E-mail</label>
            <input id="user-email" v-model="email" type="email" autocomplete="email" />
          </div>
          <div class="form-field">
            <label for="user-role">Papel</label>
            <select id="user-role" v-model="role">
              <option value="USER">Usuário</option>
              <option value="ANALYST">Analista</option>
              <option value="ADMIN">Administrador</option>
            </select>
          </div>
          <div class="form-actions">
            <button class="btn btn-primary" :disabled="saving" @click="saveChanges">
              <UiIcon name="check" :size="17" /> {{ saving ? 'Salvando...' : 'Salvar alterações' }}
            </button>
          </div>
        </section>

        <div class="security-column">
          <section class="card form-card security-card">
            <div class="card-heading">
              <span><UiIcon name="shield" :size="18" /></span>
              <div><h2>Segurança</h2><p>Defina uma nova senha de acesso.</p></div>
            </div>
            <div class="form-field">
              <label for="new-password">Nova senha</label>
              <input id="new-password" v-model="newPassword" type="password" autocomplete="new-password" placeholder="Mínimo de 6 caracteres" />
            </div>
            <button class="btn btn-secondary" :disabled="resettingPassword" @click="handleResetPassword">
              <UiIcon name="shield" :size="16" /> {{ resettingPassword ? 'Redefinindo...' : 'Redefinir senha' }}
            </button>
          </section>

          <section class="card danger-zone">
            <div class="danger-copy">
              <span><UiIcon name="trash" :size="18" /></span>
              <div><h2>Zona de risco</h2><p>A exclusão é definitiva e pode ser bloqueada pelas regras de integridade.</p></div>
            </div>
            <button class="btn btn-danger" @click="deleteDialogOpen = true"><UiIcon name="trash" :size="16" /> Excluir usuário</button>
          </section>
        </div>
      </div>
    </template>

    <UiConfirmDialog
      v-model="deleteDialogOpen"
      title="Excluir usuário"
      message="Tem certeza de que deseja excluir este usuário? Esta ação não pode ser desfeita."
      confirm-label="Excluir"
      danger
      :loading="deleting"
      @confirm="confirmDelete"
    />
  </div>
</template>

<style scoped>
.loading-layout { display: grid; gap: 20px; }
.loading-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }
.user-hero { display: flex; align-items: center; justify-content: space-between; gap: 20px; overflow: hidden; margin-bottom: 20px; padding: clamp(20px, 3vw, 27px); }
.user-hero::before { content: ''; position: absolute; inset: 0 auto 0 0; width: 3px; background: linear-gradient(180deg, var(--color-primary), var(--color-accent)); }
.identity-group { display: flex; align-items: center; gap: 17px; min-width: 0; }
.avatar-xl { width: 68px; height: 68px; display: grid; place-items: center; flex-shrink: 0; color: var(--button-primary-text); background: linear-gradient(145deg, var(--button-primary-start), var(--color-primary)); border: 1px solid var(--color-primary-border); border-radius: 18px; box-shadow: var(--shadow-primary); font-size: 1.5rem; font-weight: 800; }
.user-kicker { display: flex; align-items: center; gap: 6px; margin: 0 0 5px; color: var(--color-accent); font-size: .59rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
.user-hero h1 { margin: 0; }
.user-email { margin: 4px 0 0; color: var(--color-text-muted); font-size: .72rem; }
.user-badges { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.active-badge { color: var(--color-success); background: var(--color-success-light); }
.inactive-badge { color: var(--color-danger); background: var(--color-danger-light); }
.cards-grid { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(280px, .85fr); gap: 20px; align-items: start; }
.security-column { display: grid; gap: 20px; }
.form-card, .danger-zone { padding: clamp(20px, 3vw, 26px); }
.card-heading { display: flex; align-items: center; gap: 11px; margin-bottom: 22px; padding-bottom: 16px; border-bottom: 1px solid var(--color-border); }
.card-heading > span { width: 38px; height: 38px; display: grid; place-items: center; flex-shrink: 0; color: var(--color-primary); background: var(--color-primary-light); border-radius: 10px; }
.card-heading h2, .danger-copy h2 { margin: 0; font-size: .92rem; }
.card-heading p, .danger-copy p { margin: 4px 0 0; color: var(--color-text-muted); font-size: .63rem; line-height: 1.5; }
.form-actions { display: flex; justify-content: flex-end; padding-top: 8px; }
.security-card .btn { width: 100%; }
.danger-zone { display: flex; align-items: center; justify-content: space-between; gap: 16px; border-color: rgba(217, 54, 69, .22); background: linear-gradient(145deg, rgba(217, 54, 69, .045), transparent 50%), var(--color-surface); }
.danger-copy { display: flex; align-items: flex-start; gap: 11px; }
.danger-copy > span { width: 37px; height: 37px; display: grid; place-items: center; flex-shrink: 0; color: var(--color-danger); background: var(--color-danger-light); border-radius: 10px; }
.back-icon { transform: rotate(180deg); }
@media (max-width: 900px) { .cards-grid, .loading-grid { grid-template-columns: 1fr; } }
@media (max-width: 620px) {
  .user-hero, .identity-group, .danger-zone { align-items: flex-start; }
  .user-hero, .danger-zone { flex-direction: column; }
  .user-hero .btn, .danger-zone .btn { width: 100%; }
  .identity-group { flex-direction: column; }
}
</style>
