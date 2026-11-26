<script setup lang="ts">
const { user, logout } = useAuth()
const route = useRoute()
const toast = useToast()
const themeStore = useThemeStore()
const mobileMenuOpen = ref(false)
const userMenuOpen = ref(false)

const titles: { test: (path: string) => boolean; title: string; eyebrow: string }[] = [
  { test: (path) => path === '/dashboard', title: 'Dashboard', eyebrow: 'Visão geral' },
  { test: (path) => path === '/solicitacoes', title: 'Solicitações', eyebrow: 'Operação' },
  { test: (path) => path === '/solicitacoes/nova', title: 'Nova solicitação', eyebrow: 'Operação' },
  { test: (path) => path.includes('/editar'), title: 'Editar solicitação', eyebrow: 'Operação' },
  { test: (path) => /^\/solicitacoes\/\d+/.test(path), title: 'Detalhes da solicitação', eyebrow: 'Operação' },
  { test: (path) => path.startsWith('/admin/usuarios'), title: 'Gestão de usuários', eyebrow: 'Administração' },
  { test: (path) => path === '/perfil', title: 'Meu perfil', eyebrow: 'Conta' },
]

const pageInfo = computed(() => titles.find((item) => item.test(route.path)) || { title: 'Central', eyebrow: 'Nexotiva' })
const roleLabel = computed(() => ({ ADMIN: 'Administrador', ANALYST: 'Analista', USER: 'Usuário' })[user.value?.role || 'USER'])
const isDark = computed(() => themeStore.isDark)
const themeActionLabel = computed(() => isDark.value ? 'Ativar tema claro' : 'Ativar tema escuro')

async function toggleTheme() {
  try {
    await themeStore.toggle()
  } catch (error) {
    toast.error(extractErrorMessage(error, 'Não foi possível salvar a preferência de tema.'))
  }
}

watch(() => route.path, () => {
  userMenuOpen.value = false
  mobileMenuOpen.value = false
})
</script>

<template>
  <header class="header">
    <div class="header-inner">
      <div class="header-context">
        <button class="mobile-toggle" aria-label="Abrir menu" @click="mobileMenuOpen = true">
          <UiIcon name="menu" :size="21" />
        </button>
        <div>
          <span class="eyebrow">{{ pageInfo.eyebrow }}</span>
          <strong>{{ pageInfo.title }}</strong>
        </div>
      </div>

      <div class="header-actions">
        <span class="environment-chip"><span /> Atendimento Nexotiva</span>

        <button
          class="theme-toggle"
          type="button"
          :title="themeActionLabel"
          :aria-label="themeActionLabel"
          :disabled="themeStore.saving"
          @click="toggleTheme"
        >
          <span class="theme-icon">
            <UiIcon :name="isDark ? 'sun' : 'moon'" :size="18" />
          </span>
          <span class="theme-copy">
            <small>Tema</small>
            <strong>{{ isDark ? 'Escuro' : 'Claro' }}</strong>
          </span>
        </button>

        <div class="user-menu">
          <button class="user-trigger" :aria-expanded="userMenuOpen" @click="userMenuOpen = !userMenuOpen">
            <span class="avatar">{{ user?.name?.charAt(0)?.toUpperCase() ?? '?' }}</span>
            <span class="user-copy">
              <strong>{{ user?.name }}</strong>
              <small>{{ roleLabel }}</small>
            </span>
            <UiIcon name="chevronDown" :size="15" />
          </button>
          <div v-if="userMenuOpen" class="user-dropdown" @click="userMenuOpen = false">
            <div class="dropdown-heading">
              <span>Conta conectada</span>
              <strong>{{ user?.email }}</strong>
            </div>
            <NuxtLink to="/perfil" class="dropdown-item">
              <UiIcon name="user" :size="17" /> Meu perfil
            </NuxtLink>
            <button class="dropdown-item logout-item" @click="logout">
              <UiIcon name="logout" :size="17" /> Sair do sistema
            </button>
          </div>
        </div>
      </div>
    </div>
    <LayoutMobileMenu v-model="mobileMenuOpen" />
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 50;
  height: var(--header-height);
  border-bottom: 1px solid var(--color-border);
  background: var(--header-glass);
  backdrop-filter: blur(18px);
}
.header-inner {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 0 30px;
}
.header-context {
  display: flex;
  align-items: center;
  gap: 13px;
  min-width: 0;
}
.header-context > div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.eyebrow {
  color: var(--color-primary);
  font-size: 0.61rem;
  font-weight: 700;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}
.header-context strong {
  color: var(--color-text-soft);
  font-size: 0.89rem;
}
.mobile-toggle {
  display: none;
  width: 42px;
  height: 42px;
  place-items: center;
  color: var(--color-text-soft);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.environment-chip {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 7px 11px;
  color: var(--color-text-muted);
  background: var(--surface-translucent);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  font-size: 0.66rem;
  font-weight: 600;
}
.environment-chip span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-primary);
  box-shadow: 0 0 8px var(--color-primary);
}
.theme-toggle {
  min-height: 45px;
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 5px 11px 5px 6px;
  color: var(--color-text-soft);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.theme-toggle:hover:not(:disabled) {
  color: var(--color-primary);
  border-color: var(--color-primary-border);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}
.theme-toggle:disabled {
  opacity: 0.6;
  cursor: wait;
}
.theme-icon {
  width: 33px;
  height: 33px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  color: var(--color-primary);
  background: var(--color-primary-light);
  border-radius: 9px;
}
.theme-copy {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1px;
}
.theme-copy small {
  color: var(--color-text-muted);
  font-size: 0.56rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.theme-copy strong {
  color: var(--color-text-soft);
  font-size: 0.68rem;
}
.user-menu { position: relative; }
.user-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px 6px 6px;
  color: var(--color-text-soft);
  background: transparent;
  border: 1px solid transparent;
  border-radius: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.user-trigger:hover,
.user-trigger[aria-expanded='true'] {
  background: var(--color-surface);
  border-color: var(--color-border);
}
.avatar {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  color: var(--avatar-text);
  background: linear-gradient(145deg, var(--color-primary), var(--avatar-end));
  border-radius: 11px;
  font-size: 0.85rem;
  font-weight: 800;
  box-shadow: var(--avatar-shadow);
}
.user-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}
.user-copy strong {
  max-width: 150px;
  overflow: hidden;
  color: var(--color-text);
  font-size: 0.75rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-copy small {
  color: var(--color-text-muted);
  font-size: 0.62rem;
}
.user-dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 240px;
  overflow: hidden;
  padding: 7px;
  background: linear-gradient(180deg, var(--color-surface-soft), var(--color-surface));
  border: 1px solid var(--color-border-strong);
  border-radius: 15px;
  box-shadow: var(--shadow-lg);
}
.dropdown-heading {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 11px 12px;
  margin-bottom: 5px;
  border-bottom: 1px solid var(--color-border);
}
.dropdown-heading span {
  color: var(--color-text-muted);
  font-size: 0.61rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.dropdown-heading strong {
  overflow: hidden;
  color: var(--color-text-soft);
  font-size: 0.69rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 10px 11px;
  color: var(--color-text-soft);
  background: transparent;
  border: none;
  border-radius: 9px;
  text-align: left;
  text-decoration: none;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}
.dropdown-item:hover {
  color: var(--color-primary);
  background: var(--color-primary-light);
}
.logout-item:hover {
  color: var(--color-danger);
  background: var(--color-danger-light);
}

@media (max-width: 1080px) {
  .environment-chip { display: none; }
}
@media (max-width: 900px) {
  .header-inner { padding: 0 18px; }
  .mobile-toggle { display: grid; }
}
@media (max-width: 700px) {
  .theme-copy { display: none; }
  .theme-toggle { width: 43px; padding: 5px; justify-content: center; }
}
@media (max-width: 640px) {
  .user-copy,
  .user-trigger > svg { display: none; }
  .header-context strong { font-size: 0.8rem; }
  .header-actions { gap: 6px; }
}
</style>
