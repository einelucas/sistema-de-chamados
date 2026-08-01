<script setup lang="ts">
// Página raiz: redireciona para o dashboard (se autenticado) ou para o login.
definePageMeta({ layout: false })

const authStore = useAuthStore()

onMounted(() => {
  navigateTo(authStore.isAuthenticated ? '/dashboard' : '/login')
})
</script>

<template>
  <div />
</template>
