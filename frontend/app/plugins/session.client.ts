// Restaura a sessão do usuário (token salvo) assim que a aplicação carrega no navegador.
export default defineNuxtPlugin(async () => {
  const authStore = useAuthStore()
  await authStore.restoreSession()
})
