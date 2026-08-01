// Store de autenticação. Usado porque o estado de sessão é global e compartilhado
// por toda a aplicação (header, sidebar, middlewares de rota, etc).
import { defineStore } from 'pinia'
import type { User } from '~/types/user'

interface AuthState {
  token: string | null
  user: User | null
  initialized: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: null,
    user: null,
    initialized: false,
  }),

  getters: {
    isAuthenticated: (state) => Boolean(state.token && state.user),
    isAdmin: (state) => state.user?.role === 'ADMIN',
    isAnalystOrAdmin: (state) => state.user?.role === 'ADMIN' || state.user?.role === 'ANALYST',
  },

  actions: {
    setSession(token: string, user: User) {
      this.token = token
      this.user = user
      useThemeStore().syncFromUser(user)
      if (import.meta.client) {
        window.sessionStorage.setItem('central_token', token)
      }
    },

    setUser(user: User) {
      this.user = user
      useThemeStore().syncFromUser(user)
    },

    logout() {
      this.token = null
      this.user = null
      if (import.meta.client) {
        window.sessionStorage.removeItem('central_token')
      }
      navigateTo('/login')
    },

    // Restaura a sessão a partir do armazenamento local (chamado no plugin de inicialização).
    async restoreSession() {
      if (this.initialized) return
      this.initialized = true

      if (!import.meta.client) return
      const storedToken = window.sessionStorage.getItem('central_token')
      if (!storedToken) return

      this.token = storedToken
      try {
        const { $api } = useNuxtApp()
        const user = await $api<User>('/auth/me')
        this.user = user
        useThemeStore().syncFromUser(user)
      } catch {
        this.token = null
        this.user = null
        window.sessionStorage.removeItem('central_token')
      }
    },
  },
})
