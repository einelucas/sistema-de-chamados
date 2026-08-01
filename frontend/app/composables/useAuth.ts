// Composable de autenticação: login, logout e acesso ao usuário atual.
import type { User } from '~/types/user'

interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export function useAuth() {
  const authStore = useAuthStore()
  const { $api } = useNuxtApp()

  async function login(email: string, password: string) {
    const response = await $api<LoginResponse>('/auth/login', {
      method: 'POST',
      body: { email, password },
    })
    authStore.setSession(response.access_token, response.user)
    return response.user
  }

  function logout() {
    authStore.logout()
  }

  return {
    login,
    logout,
    user: computed(() => authStore.user),
    isAuthenticated: computed(() => authStore.isAuthenticated),
    isAdmin: computed(() => authStore.isAdmin),
    isAnalystOrAdmin: computed(() => authStore.isAnalystOrAdmin),
  }
}
