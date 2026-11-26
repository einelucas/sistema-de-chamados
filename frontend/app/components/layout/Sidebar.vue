<script setup lang="ts">
const { isAdmin } = useAuth()
const route = useRoute()

const links = computed(() => {
  const base = [
    { to: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
    { to: '/solicitacoes', label: 'Solicitações', icon: 'requests' },
    { to: '/perfil', label: 'Meu perfil', icon: 'user' },
  ]

  if (isAdmin.value) {
    base.splice(2, 0, { to: '/admin/usuarios', label: 'Usuários', icon: 'users' })
  }

  return base
})

function isActive(path: string) {
  return route.path === path || (path !== '/dashboard' && route.path.startsWith(path))
}
</script>

<template>
  <aside class="sidebar">
    <NuxtLink to="/dashboard" class="brand" aria-label="Ir para o dashboard">
      <img src="~/assets/brand/logo.png" class="nexotiva-logo" alt="Nexotiva" />
    </NuxtLink>

    <div class="nav-section">
      <p class="nav-label">Navegação</p>
      <nav class="nav">
        <NuxtLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="nav-link"
          :class="{ active: isActive(link.to) }"
        >
          <span class="nav-icon"><UiIcon :name="link.icon" :size="19" /></span>
          <span>{{ link.label }}</span>
          <span v-if="isActive(link.to)" class="active-indicator" />
        </NuxtLink>
      </nav>
    </div>

    <div class="sidebar-footer">
      <div class="system-status">
        <span class="status-dot" />
        <div>
          <strong>Sistema operacional</strong>
          <span>Central de atendimento</span>
        </div>
      </div>
      <span class="version">Central v1.0</span>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 60;
  width: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  padding: 24px 18px 18px;
  overflow-y: auto;
  background:
    linear-gradient(180deg, rgba(var(--primary-rgb), 0.045), transparent 24%),
    var(--color-surface);
  border-right: 1px solid var(--color-border);
}
.brand {
  display: flex;
  align-items: center;
  gap: 13px;
  min-height: 64px;
  padding: 0 9px 22px;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
  text-decoration: none;
}
.brand-mark {
  position: relative;
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  overflow: hidden;
  border: 1px solid var(--brand-mark-border);
  border-radius: 13px;
  background: var(--brand-mark-bg);
  box-shadow: var(--avatar-shadow), inset 0 1px 0 var(--card-inset);
}
.brand-mark-line {
  position: absolute;
  width: 22px;
  height: 4px;
  left: 9px;
  top: 20px;
  border-radius: 999px;
  background: var(--color-primary);
  transform: rotate(-38deg);
  box-shadow: 0 -8px 0 var(--brand-secondary-line), 0 8px 0 var(--brand-accent-line);
}
.brand-mark-dot {
  position: absolute;
  right: 7px;
  top: 7px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--color-accent);
  box-shadow: 0 0 12px var(--brand-accent-glow);
}
.brand-copy {
  display: flex;
  flex-direction: column;
  line-height: 1.05;
}
.brand-copy strong {
  color: var(--color-primary);
  font-family: 'Manrope', sans-serif;
  font-size: 0.98rem;
  font-weight: 400;
  letter-spacing: 0.06em;
}
.brand-copy span {
  margin-top: 5px;
  color: var(--color-text-soft);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.17em;
}
.nav-section {
  flex: 1;
  padding-top: 26px;
}
.nav-label {
  margin: 0 12px 10px;
  color: var(--color-text-muted);
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.nav {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 48px;
  padding: 10px 13px;
  overflow: hidden;
  color: var(--color-text-muted);
  border: 1px solid transparent;
  border-radius: 13px;
  text-decoration: none;
  font-size: 0.82rem;
  font-weight: 600;
  transition: all var(--transition-base);
}
.nav-link:hover {
  color: var(--color-text);
  background: var(--color-surface-soft);
  border-color: var(--color-border);
  transform: translateX(2px);
}
.nav-link.active {
  color: var(--nav-active-text);
  background: linear-gradient(135deg, var(--button-primary-start), var(--color-primary));
  border-color: var(--color-primary-border);
  box-shadow: var(--shadow-primary);
}
.nav-icon {
  width: 27px;
  height: 27px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  border-radius: 8px;
  color: currentColor;
  background: var(--color-bg-soft);
}
.nav-link.active .nav-icon {
  background: var(--nav-active-icon-bg);
}
.active-indicator {
  position: absolute;
  right: 9px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--nav-indicator);
}
.sidebar-footer {
  padding: 16px 8px 2px;
  border-top: 1px solid var(--color-border);
}
.system-status {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 10px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--surface-translucent);
}
.status-dot {
  width: 8px;
  height: 8px;
  flex-shrink: 0;
  border-radius: 50%;
  background: var(--color-primary);
  box-shadow: 0 0 12px rgba(var(--primary-rgb), 0.68);
}
.system-status div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.system-status strong {
  color: var(--color-text-soft);
  font-size: 0.68rem;
}
.system-status div span,
.version {
  color: var(--color-text-muted);
  font-size: 0.61rem;
}
.version {
  display: block;
  margin-top: 10px;
  padding-left: 10px;
}

@media (max-width: 900px) {
  .sidebar { display: none; }
}
</style>
