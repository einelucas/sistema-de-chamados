<script setup lang="ts">
// Layout principal com navegação lateral fixa e área de trabalho responsiva.
</script>

<template>
  <div class="app-shell">
    <LayoutSidebar />
    <div class="workspace">
      <LayoutHeader />
      <main class="app-content">
        <div class="container">
          <slot />
        </div>
      </main>
    </div>
    <UiToastContainer />
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
}
.workspace {
  min-height: 100vh;
  margin-left: var(--sidebar-width);
}
.app-content {
  min-width: 0;
  padding: 30px 0 54px;
}

@media (max-width: 900px) {
  .workspace {
    margin-left: 0;
  }
  .app-content {
    padding-top: 22px;
  }
}
</style>
