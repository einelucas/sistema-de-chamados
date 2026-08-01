<script setup lang="ts">
// Bloco skeleton simples para indicar carregamento de conteúdo.
withDefaults(defineProps<{ height?: string; width?: string; rounded?: boolean }>(), {
  height: '16px',
  width: '100%',
})
</script>

<template>
  <div class="skeleton" :style="{ height, width }" />
</template>
