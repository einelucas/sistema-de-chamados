<script setup lang="ts">
withDefaults(
  defineProps<{ title: string; description?: string; icon?: string }>(),
  { icon: 'folder' },
)
</script>

<template>
  <div class="empty-state">
    <span class="empty-icon"><UiIcon :name="icon" :size="27" /></span>
    <h4>{{ title }}</h4>
    <p v-if="description">{{ description }}</p>
    <slot name="action" />
  </div>
</template>

<style scoped>
.empty-icon {
  width: 58px;
  height: 58px;
  display: grid;
  place-items: center;
  margin-bottom: 4px;
  color: var(--color-primary);
  background: var(--color-primary-light);
  border: 1px solid var(--color-primary-border);
  border-radius: 17px;
  box-shadow: 0 14px 32px rgba(var(--primary-rgb), 0.08);
}
</style>
