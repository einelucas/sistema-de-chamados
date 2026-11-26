// Middleware para a página de login: se já autenticado, redireciona ao dashboard.
export default defineNuxtRouteMiddleware(() => {
  const authStore = useAuthStore()
  if (authStore.isAuthenticated) {
    return navigateTo(authStore.user?.must_change_password?'/primeiro-acesso':'/dashboard')
  }
})
