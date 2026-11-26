<script setup lang="ts">
// Página de criação de um novo usuário (área administrativa).
definePageMeta({ middleware: 'admin' })

const { createUser } = useUsers()
const toast = useToast()

const name = ref('')
const email = ref('')
const password = ref('')
const role = ref<'ADMIN' | 'ANALYST' | 'USER'>('USER')
const loading = ref(false)
const errors = ref<{ name?: string; email?: string; password?: string }>({})

function validate(): boolean {
  errors.value = {}
  if (name.value.trim().length < 2) errors.value.name = 'Informe o nome completo.'
  if (!email.value.includes('@')) errors.value.email = 'Informe um e-mail válido.'
  if (password.value.length < 6) errors.value.password = 'A senha deve ter ao menos 6 caracteres.'
  return Object.keys(errors.value).length === 0
}

async function handleSubmit() {
  if (!validate()) return
  loading.value = true
  try {
    await createUser({ name: name.value.trim(), email: email.value.trim(), password: password.value, role: role.value })
    toast.success('Usuário criado com sucesso.')
    await navigateTo('/admin/usuarios')
  } catch (error) {
    toast.error(extractErrorMessage(error, 'Não foi possível criar o usuário.'))
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <LayoutBreadcrumbs
      :items="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Usuários', to: '/admin/usuarios' }, { label: 'Novo' }]"
    />

    <div class="page-header">
      <div>
        <h1>Novo usuário</h1>
        <p>Cadastre um novo acesso e defina o nível de permissão inicial.</p>
      </div>
      <VBtn to="/admin/usuarios" class="hub-action-button" color="secondary" variant="outlined">
        <UiIcon name="arrowRight" :size="17" class="back-icon" /> Voltar aos usuários
      </VBtn>
    </div>

    <div class="user-form-layout">
      <form class="card form-card" @submit.prevent="handleSubmit">
        <div class="form-heading">
          <span><UiIcon name="user" :size="19" /></span>
          <div><h2>Dados de acesso</h2><p>As credenciais poderão ser alteradas posteriormente.</p></div>
        </div>

        <div class="form-field">
          <label for="name">Nome completo</label>
          <input id="name" v-model="name" type="text" autocomplete="name" placeholder="Nome e sobrenome" />
          <span v-if="errors.name" class="form-error">{{ errors.name }}</span>
        </div>
        <div class="form-field">
          <label for="email">E-mail</label>
          <input id="email" v-model="email" type="email" autocomplete="email" placeholder="nome@empresa.com" />
          <span v-if="errors.email" class="form-error">{{ errors.email }}</span>
        </div>
        <div class="form-field">
          <label for="password">Senha inicial</label>
          <input id="password" v-model="password" type="password" autocomplete="new-password" placeholder="Mínimo de 6 caracteres" />
          <span v-if="errors.password" class="form-error">{{ errors.password }}</span>
        </div>
        <div class="form-field">
          <label for="role">Papel</label>
          <VSelect id="role" v-model="role" :items="[{title:'Usuário',value:'USER'},{title:'Analista',value:'ANALYST'},{title:'Administrador',value:'ADMIN'}]" hide-details/>
        </div>

        <div class="form-actions">
          <VBtn class="hub-action-button" color="primary" variant="flat" type="submit" :disabled="loading">
            <UiIcon name="check" :size="17" /> {{ loading ? 'Criando...' : 'Criar usuário' }}
          </VBtn>
        </div>
      </form>

      <aside class="card permissions-card">
        <span class="permissions-icon"><UiIcon name="shield" :size="20" /></span>
        <p class="eyebrow">Controle de acesso</p>
        <h2>Escolha o papel com atenção</h2>
        <div class="role-guide">
          <div><strong>Usuário</strong><p>Abre e acompanha as próprias solicitações.</p></div>
          <div><strong>Analista</strong><p>Atende, prioriza e conclui solicitações.</p></div>
          <div><strong>Administrador</strong><p>Possui acesso total e gerencia usuários.</p></div>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.user-form-layout { display: grid; grid-template-columns: minmax(0, 620px) minmax(240px, 330px); gap: 20px; align-items: start; }
.form-card { padding: clamp(20px, 3vw, 28px); }
.form-heading { display: flex; align-items: center; gap: 11px; margin-bottom: 24px; padding-bottom: 17px; border-bottom: 1px solid var(--color-border); }
.form-heading > span, .permissions-icon { width: 40px; height: 40px; display: grid; place-items: center; flex-shrink: 0; color: var(--color-primary); background: var(--color-primary-light); border-radius: 11px; }
.form-heading h2 { margin: 0; font-size: .92rem; }
.form-heading p { margin: 4px 0 0; color: var(--color-text-muted); font-size: .64rem; }
.form-actions { display: flex; justify-content: flex-end; margin-top: 8px; padding-top: 20px; border-top: 1px solid var(--color-border); }
.form-actions .btn { min-width: 170px; }
.permissions-card { overflow: hidden; padding: 24px; }
.permissions-card::before { content: ''; position: absolute; inset: 0 0 auto; height: 2px; background: linear-gradient(90deg, var(--color-primary), var(--color-accent)); }
.permissions-icon { margin-bottom: 18px; color: var(--color-accent); background: var(--color-accent-light); }
.eyebrow { margin: 0 0 7px; color: var(--color-accent); font-size: .59rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
.permissions-card h2 { font-size: 1rem; }
.role-guide { display: grid; gap: 12px; margin-top: 18px; }
.role-guide > div { padding: 12px; background: var(--surface-translucent); border: 1px solid var(--color-border); border-radius: 11px; }
.role-guide strong { color: var(--color-text-soft); font-size: .7rem; }
.role-guide p { margin: 4px 0 0; color: var(--color-text-muted); font-size: .62rem; line-height: 1.55; }
.back-icon { transform: rotate(180deg); }
@media (max-width: 900px) { .user-form-layout { grid-template-columns: 1fr; } }
@media (max-width: 560px) { .form-actions .btn { width: 100%; } }
</style>
