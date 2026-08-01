// Plugin que expõe um cliente $api centralizado (ofetch) já configurado com a base
// da API e o token de autenticação, para não espalhar URLs pelos componentes.
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  const api = $fetch.create({
    baseURL: config.public.apiBase,
    onRequest({ options }) {
      const authStore = useAuthStore()
      if (authStore.token) {
        options.headers = new Headers(options.headers)
        options.headers.set('Authorization', `Bearer ${authStore.token}`)
      }
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        const authStore = useAuthStore()
        if (authStore.isAuthenticated) {
          authStore.logout()
        }
      }
    },
  })

  return {
    provide: {
      api,
    },
  }
})
