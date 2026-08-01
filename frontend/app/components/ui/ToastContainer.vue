<script setup lang="ts">
const { toasts, remove } = useToast()

const iconFor = (type: string) => type === 'success' ? 'check' : type === 'error' ? 'open' : 'activity'
</script>

<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div v-for="toast in toasts" :key="toast.id" class="toast" :class="`toast-${toast.type}`">
          <span class="toast-icon"><UiIcon :name="iconFor(toast.type)" :size="18" /></span>
          <span class="toast-message">{{ toast.message }}</span>
          <button class="toast-close" aria-label="Fechar notificação" @click="remove(toast.id)">
            <UiIcon name="close" :size="16" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast {
  justify-content: flex-start;
  color: var(--color-text-soft);
}
.toast-icon {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  color: currentColor;
  background: color-mix(in srgb, currentColor 12%, transparent);
  border-radius: 9px;
}
.toast-message {
  flex: 1;
  color: var(--color-text);
  line-height: 1.45;
}
.toast-close {
  display: grid;
  place-items: center;
}
.toast-success { color: var(--color-success); }
.toast-error { color: var(--color-danger); }
.toast-info { color: var(--color-primary); }
.toast-enter-active,
.toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from,
.toast-leave-to { opacity: 0; transform: translateX(20px); }
</style>
