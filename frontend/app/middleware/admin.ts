// Middleware que restringe páginas administrativas a usuários com papel ADMIN.
export default defineNuxtRouteMiddleware(() => {
  const authStore = useAuthStore()

  if (!authStore.isAuthenticated) {
    return navigateTo('/login')
  }
  if (!authStore.isAdmin) {
    return navigateTo('/dashboard')
  }
})
