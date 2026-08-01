<script setup lang="ts">
const props = defineProps<{ page: number; totalPages: number; total: number }>()
const emit = defineEmits<{ 'update:page': [page: number] }>()

function go(page: number) {
  if (page >= 1 && page <= props.totalPages) emit('update:page', page)
}
</script>

<template>
  <div v-if="totalPages > 1" class="pagination">
    <span class="total-label"><strong>{{ total }}</strong> resultado(s)</span>
    <div class="controls">
      <button class="page-button" :disabled="page === 1" aria-label="Página anterior" @click="go(page - 1)">
        <UiIcon name="arrowRight" :size="16" class="arrow-back" />
      </button>
      <span class="page-indicator"><strong>{{ page }}</strong><span>/</span>{{ totalPages }}</span>
      <button class="page-button" :disabled="page === totalPages" aria-label="Próxima página" @click="go(page + 1)">
        <UiIcon name="arrowRight" :size="16" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 16px;
  padding: 11px 13px;
  color: var(--color-text-muted);
  background: var(--surface-translucent);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  font-size: 0.66rem;
}
.total-label strong { color: var(--color-text-soft); }
.controls { display: flex; align-items: center; gap: 8px; }
.page-button {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  color: var(--color-text-soft);
  background: var(--color-surface-soft);
  border: 1px solid var(--color-border-strong);
  border-radius: 9px;
  cursor: pointer;
}
.page-button:hover:not(:disabled) { color: var(--color-primary); border-color: var(--color-primary-border); }
.page-button:disabled { opacity: 0.35; cursor: not-allowed; }
.arrow-back { transform: rotate(180deg); }
.page-indicator { min-width: 55px; display: flex; justify-content: center; gap: 5px; }
.page-indicator strong { color: var(--color-primary); }
.page-indicator span { color: var(--color-text-muted); }
@media (max-width: 500px) {
  .pagination { align-items: stretch; flex-direction: column; }
  .controls { justify-content: space-between; }
}
</style>
