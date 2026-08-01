// Aplica a preferência local antes da restauração da sessão para reduzir mudanças visuais tardias.
export default defineNuxtPlugin(() => {
  const themeStore = useThemeStore()
  themeStore.initialize()
})
