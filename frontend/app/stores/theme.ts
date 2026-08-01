import { defineStore } from 'pinia'
import type { ThemePreference, User } from '~/types/user'

const STORAGE_KEY = 'central_theme'

function isThemePreference(value: string | null): value is ThemePreference {
  return value === 'light' || value === 'dark'
}

interface ThemeState {
  preference: ThemePreference
  initialized: boolean
  saving: boolean
}

export const useThemeStore = defineStore('theme', {
  state: (): ThemeState => ({
    preference: 'light',
    initialized: false,
    saving: false,
  }),

  getters: {
    isDark: (state) => state.preference === 'dark',
  },

  actions: {
    applyTheme(preference: ThemePreference) {
      this.preference = preference
      if (!import.meta.client) return

      document.documentElement.dataset.theme = preference
      document.documentElement.style.colorScheme = preference
      window.localStorage.setItem(STORAGE_KEY, preference)
    },

    initialize() {
      if (this.initialized || !import.meta.client) return

      const storedPreference = window.localStorage.getItem(STORAGE_KEY)
      this.applyTheme(isThemePreference(storedPreference) ? storedPreference : 'light')
      this.initialized = true
    },

    syncFromUser(user: User | null) {
      if (!user?.theme_preference) return
      this.applyTheme(user.theme_preference)
    },

    async setPreference(preference: ThemePreference) {
      const previousPreference = this.preference
      this.applyTheme(preference)

      const authStore = useAuthStore()
      if (!authStore.isAuthenticated) return

      this.saving = true
      try {
        const { $api } = useNuxtApp()
        const updatedUser = await $api<User>('/users/me/theme', {
          method: 'PATCH',
          body: { theme_preference: preference },
        })
        authStore.setUser(updatedUser)
      } catch (error) {
        this.applyTheme(previousPreference)
        throw error
      } finally {
        this.saving = false
      }
    },

    async toggle() {
      await this.setPreference(this.isDark ? 'light' : 'dark')
    },
  },
})
