<script setup lang="ts">
// Página de perfil: exibe os dados do usuário autenticado.
definePageMeta({ middleware: 'auth' })
const { user } = useAuth()

const roleDescription = computed(() => {
  const descriptions = {
    ADMIN: 'Acesso administrativo completo à Central de Solicitações.',
    ANALYST: 'Responsável pelo tratamento e acompanhamento das solicitações.',
    USER: 'Acesso para abertura e acompanhamento das próprias solicitações.',
  }
  return descriptions[user.value?.role || 'USER']
})
</script>

<template>
  <div>
    <LayoutBreadcrumbs :items="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Meu perfil' }]" />

    <div class="page-header">
      <div>
        <h1>Meu perfil</h1>
        <p>Consulte seus dados de acesso e o nível de permissão atual.</p>
      </div>
    </div>

    <div v-if="user" class="profile-layout">
      <section class="card profile-hero">
        <div class="profile-pattern" />
        <div class="profile-content">
          <span class="avatar-lg">{{ user.name.charAt(0).toUpperCase() }}</span>
          <div class="profile-info">
            <p class="eyebrow"><UiIcon name="user" :size="14" /> Identidade do usuário</p>
            <h2>{{ user.name }}</h2>
            <p class="profile-email">{{ user.email }}</p>
            <div class="profile-badges">
              <UiRoleBadge :role="user.role" />
              <span class="badge" :class="user.is_active ? 'active-badge' : 'inactive-badge'">{{ user.is_active ? 'Ativo' : 'Inativo' }}</span>
            </div>
          </div>
        </div>
      </section>

      <aside class="profile-side">
        <section class="card info-panel">
          <div class="panel-heading">
            <span><UiIcon name="shield" :size="18" /></span>
            <div><h2>Acesso e permissões</h2><p>{{ roleDescription }}</p></div>
          </div>
          <div class="info-row">
            <span>Perfil</span>
            <UiRoleBadge :role="user.role" />
          </div>
          <div class="info-row">
            <span>Status da conta</span>
            <strong :class="user.is_active ? 'status-active' : 'status-inactive'">{{ user.is_active ? 'Conta ativa' : 'Conta inativa' }}</strong>
          </div>
          <div class="info-row">
            <span>Membro desde</span>
            <strong>{{ formatDateOnly(user.created_at) }}</strong>
          </div>
        </section>

        <section class="card help-panel">
          <UiIcon name="activity" :size="18" />
          <div><strong>Precisa alterar seus dados?</strong><p>Entre em contato com um administrador da Central.</p></div>
        </section>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.profile-layout { display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(280px, .65fr); gap: 20px; align-items: stretch; }
.profile-hero { position: relative; min-height: 330px; overflow: hidden; padding: clamp(24px, 4vw, 38px); }
.profile-hero::before { content: ''; position: absolute; inset: 0 auto 0 0; width: 3px; background: linear-gradient(180deg, var(--color-primary), var(--color-accent)); }
.profile-pattern { position: absolute; width: 300px; height: 300px; top: -130px; right: -90px; border: 1px solid rgba(var(--primary-rgb), .14); border-radius: 50%; box-shadow: 0 0 0 42px rgba(var(--primary-rgb), .025), 0 0 0 84px rgba(var(--accent-rgb), .018); }
.profile-content { position: relative; z-index: 1; display: flex; align-items: center; gap: 22px; min-height: 250px; }
.avatar-lg { width: 94px; height: 94px; display: grid; place-items: center; flex-shrink: 0; color: var(--button-primary-text); background: linear-gradient(145deg, var(--button-primary-start), var(--color-primary)); border: 1px solid var(--color-primary-border); border-radius: 25px; box-shadow: 0 18px 45px rgba(var(--primary-rgb), .20); font-size: 2rem; font-weight: 800; }
.eyebrow { display: flex; align-items: center; gap: 6px; margin: 0 0 8px; color: var(--color-accent); font-size: .59rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
.profile-info h2 { margin: 0; font-size: clamp(1.5rem, 3vw, 2.25rem); }
.profile-email { margin: 7px 0 0; color: var(--color-text-muted); font-size: .78rem; }
.profile-badges { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 15px; }
.active-badge { color: var(--color-success); background: var(--color-success-light); }
.inactive-badge { color: var(--color-danger); background: var(--color-danger-light); }
.profile-side { display: grid; gap: 20px; }
.info-panel { padding: 22px; }
.panel-heading { display: flex; align-items: flex-start; gap: 10px; padding-bottom: 17px; border-bottom: 1px solid var(--color-border); }
.panel-heading > span { width: 38px; height: 38px; display: grid; place-items: center; flex-shrink: 0; color: var(--color-primary); background: var(--color-primary-light); border-radius: 10px; }
.panel-heading h2 { margin: 0; font-size: .88rem; }
.panel-heading p { margin: 4px 0 0; color: var(--color-text-muted); font-size: .61rem; line-height: 1.5; }
.info-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 15px 0; border-bottom: 1px solid var(--color-border); }
.info-row:last-child { border-bottom: 0; padding-bottom: 0; }
.info-row > span { color: var(--color-text-muted); font-size: .63rem; }
.info-row strong { color: var(--color-text-soft); font-size: .66rem; }
.status-active { color: var(--color-success) !important; }
.status-inactive { color: var(--color-danger) !important; }
.help-panel { display: flex; align-items: flex-start; gap: 10px; padding: 17px; color: var(--color-accent); border-color: rgba(var(--accent-rgb), .18); background: linear-gradient(145deg, rgba(var(--accent-rgb), .045), transparent 70%), var(--color-surface); }
.help-panel svg { flex-shrink: 0; }
.help-panel strong { display: block; color: var(--color-text-soft); font-size: .67rem; }
.help-panel p { margin: 4px 0 0; color: var(--color-text-muted); font-size: .6rem; line-height: 1.5; }
@media (max-width: 900px) { .profile-layout { grid-template-columns: 1fr; } .profile-hero { min-height: 260px; } }
@media (max-width: 620px) { .profile-content { align-items: flex-start; flex-direction: column; } }
</style>
