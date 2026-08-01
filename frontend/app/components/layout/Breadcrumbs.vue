<script setup lang="ts">
defineProps<{ items: { label: string; to?: string }[] }>()
</script>

<template>
  <nav class="breadcrumbs" aria-label="breadcrumb">
    <template v-for="(item, index) in items" :key="`${item.label}-${index}`">
      <NuxtLink v-if="item.to" :to="item.to" class="crumb-link">{{ item.label }}</NuxtLink>
      <span v-else class="crumb-current">{{ item.label }}</span>
      <UiIcon v-if="index < items.length - 1" name="chevronDown" :size="12" class="crumb-sep" />
    </template>
  </nav>
</template>

<style scoped>
.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 18px;
  color: var(--color-text-muted);
  font-size: 0.67rem;
  flex-wrap: wrap;
}
.crumb-link {
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color var(--transition-fast);
}
.crumb-link:hover { color: var(--color-primary); }
.crumb-current { color: var(--color-text-soft); font-weight: 700; }
.crumb-sep {
  color: var(--color-text-muted);
  transform: rotate(-90deg);
}
</style>
