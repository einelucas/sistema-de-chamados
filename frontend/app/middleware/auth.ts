// Middleware que protege páginas exigindo autenticação. Redireciona para /login quando necessário.
export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore()

  if (!authStore.isAuthenticated) {
    return navigateTo({ path: '/login', query: { redirect: to.fullPath } })
  }
  if(authStore.user?.must_change_password && to.path!=='/primeiro-acesso')return navigateTo('/primeiro-acesso')
  if(!authStore.user?.must_change_password && to.path==='/primeiro-acesso')return navigateTo('/dashboard')
})
