<script setup lang="ts">
const theme=useThemeStore()
const route=useRoute()
const currentTheme=computed(()=>route.meta.layout==='auth'?'light':theme.isDark?'dark':'light')
</script>
<template><VApp :theme="currentTheme"><NuxtLayout><NuxtPage /></NuxtLayout></VApp></template>
