// Middleware para a página de login: se já autenticado, redireciona ao dashboard.
export default defineNuxtRouteMiddleware(() => {
  const authStore = useAuthStore()
  if (authStore.isAuthenticated) {
    return navigateTo('/dashboard')
  }
})
