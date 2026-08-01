<script setup lang="ts">
const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()
const { isAdmin, logout } = useAuth()
const route = useRoute()

const links = computed(() => {
  const base = [
    { to: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
    { to: '/solicitacoes', label: 'Solicitações', icon: 'requests' },
    { to: '/perfil', label: 'Meu perfil', icon: 'user' },
  ]
  if (isAdmin.value) base.splice(2, 0, { to: '/admin/usuarios', label: 'Usuários', icon: 'users' })
  return base
})

function isActive(path: string) {
  return route.path === path || (path !== '/dashboard' && route.path.startsWith(path))
}

function close() {
  emit('update:modelValue', false)
}
</script>

<template>
  <Teleport to="body">
    <div v-if="modelValue" class="mobile-overlay" @click.self="close">
      <aside class="mobile-panel">
        <div class="mobile-brand">
          <span class="brand-mark"><span /></span>
          <div><strong>CENTRAL</strong><small>SOLICITAÇÕES</small></div>
          <button aria-label="Fechar menu" @click="close"><UiIcon name="close" :size="19" /></button>
        </div>

        <nav class="nav">
          <NuxtLink
            v-for="link in links"
            :key="link.to"
            :to="link.to"
            class="nav-link"
            :class="{ active: isActive(link.to) }"
            @click="close"
          >
            <UiIcon :name="link.icon" :size="19" />
            <span>{{ link.label }}</span>
          </NuxtLink>
        </nav>

        <div class="mobile-footer">
          <button class="btn btn-secondary" @click="logout(); close()">
            <UiIcon name="logout" :size="18" /> Sair do sistema
          </button>
        </div>
      </aside>
    </div>
  </Teleport>
</template>

<style scoped>
.mobile-panel {
  width: min(318px, 88vw);
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px 16px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border-strong);
  box-shadow: var(--shadow-lg);
  animation: drawer-in var(--transition-base);
}
.mobile-brand {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 3px 3px 20px;
  border-bottom: 1px solid var(--color-border);
}
.brand-mark {
  position: relative;
  width: 38px;
  height: 38px;
  overflow: hidden;
  border: 1px solid var(--brand-mark-border);
  border-radius: 12px;
  background: var(--color-primary-light);
}
.brand-mark span {
  position: absolute;
  left: 8px;
  top: 18px;
  width: 21px;
  height: 4px;
  border-radius: 99px;
  background: var(--color-primary);
  transform: rotate(-38deg);
  box-shadow: 0 8px 0 var(--brand-accent-line);
}
.mobile-brand > div {
  display: flex;
  flex-direction: column;
  flex: 1;
}
.mobile-brand strong {
  color: var(--color-primary);
  font-family: 'Aclonica', sans-serif;
  font-size: 0.9rem;
  font-weight: 400;
}
.mobile-brand small {
  margin-top: 3px;
  color: var(--color-text-soft);
  font-size: 0.56rem;
  font-weight: 700;
  letter-spacing: 0.15em;
}
.mobile-brand button {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  border-radius: 10px;
  cursor: pointer;
}
.mobile-brand button:hover { background: var(--color-surface-soft); color: var(--color-primary); }
.nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 22px;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 48px;
  padding: 11px 13px;
  color: var(--color-text-muted);
  border: 1px solid transparent;
  border-radius: 12px;
  text-decoration: none;
  font-size: 0.82rem;
  font-weight: 600;
}
.nav-link.active {
  color: var(--nav-active-text);
  background: linear-gradient(135deg, var(--button-primary-start), var(--color-primary));
}
.nav-link:not(.active):hover {
  color: var(--color-text);
  background: var(--color-surface-soft);
  border-color: var(--color-border);
}
.mobile-footer {
  margin-top: auto;
  padding-top: 18px;
  border-top: 1px solid var(--color-border);
}
.mobile-footer .btn { width: 100%; }
</style>
