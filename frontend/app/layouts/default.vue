<script setup lang="ts">
import { useDisplay } from 'vuetify'
const { width } = useDisplay()
const isMobile = computed(() => width.value <= 900)
const desktopOpen = ref(true)
const mobileOpen = ref(false)
const route = useRoute()
const menuOpen = computed(() => isMobile.value ? mobileOpen.value : desktopOpen.value)
function toggleMenu() {
  if (isMobile.value) mobileOpen.value = !mobileOpen.value
  else desktopOpen.value = !desktopOpen.value
}
function restoreMenuFocus() {
  if (import.meta.client) nextTick(() => document.getElementById('central-menu-toggle')?.focus())
}
function closeDesktop() {
  desktopOpen.value = false
  restoreMenuFocus()
}
watch(isMobile, () => { mobileOpen.value = false })
watch(() => route.path, () => { mobileOpen.value = false })
</script>

<template>
  <div class="app-shell" :class="{ 'sidebar-expanded': !isMobile && desktopOpen }">
    <Transition name="sidebar-slide">
      <LayoutSidebar v-if="!isMobile && desktopOpen" id="central-desktop-sidebar" @close="closeDesktop" />
    </Transition>
    <div class="workspace">
      <LayoutHeader :menu-open="menuOpen" :menu-controls="isMobile ? 'central-mobile-sidebar' : 'central-desktop-sidebar'" @toggle-menu="toggleMenu" />
      <main class="app-content">
        <div class="container"><slot /></div>
      </main>
    </div>
    <VDialog v-if="isMobile" v-model="mobileOpen" content-class="central-mobile-sidebar-dialog" transition="slide-x-transition" :width="318" :max-width="'88vw'" :scrollable="true" aria-label="Menu de navegação" @after-leave="restoreMenuFocus">
      <LayoutSidebar id="central-mobile-sidebar" mobile @close="mobileOpen = false" />
    </VDialog>
    <UiToastContainer />
  </div>
</template>

<style scoped>
.app-shell { min-height: 100vh; }
.workspace { min-height: 100vh; min-width: 0; margin-left: 0; transition: margin-left 180ms ease; }
.sidebar-expanded .workspace { margin-left: var(--sidebar-width); }
.app-content { min-width: 0; padding: 30px 0 54px; }
.sidebar-slide-enter-active,.sidebar-slide-leave-active { transition: transform 180ms ease; }
.sidebar-slide-enter-from,.sidebar-slide-leave-to { transform: translateX(-100%); }
@media (max-width:900px) {
  .sidebar-expanded .workspace { margin-left: 0; }
  .app-content { padding-top: 22px; }
}
@media (prefers-reduced-motion:reduce) {
  .workspace,.sidebar-slide-enter-active,.sidebar-slide-leave-active { transition:none; }
}
</style>

<style>
.central-mobile-sidebar-dialog.v-overlay__content {
  position:absolute; inset:0 auto 0 0; margin:0!important;
  height:100dvh!important; max-height:100dvh!important;
  border-radius:0!important; overflow:hidden;
}
</style>
