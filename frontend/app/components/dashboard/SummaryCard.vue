<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    label: string
    value: number | string
    icon?: string
    accent?: string
    eyebrow?: string
  }>(),
  {
    icon: 'total',
    accent: 'var(--color-primary)',
    eyebrow: 'Indicador',
  },
)
</script>

<template>
  <article class="summary-card card" :style="{ '--summary-accent': accent }">
    <span class="summary-line" />
    <div class="summary-top">
      <span class="summary-eyebrow">{{ eyebrow }}</span>
      <span class="summary-icon"><UiIcon :name="icon" :size="21" /></span>
    </div>
    <p class="summary-value">{{ value }}</p>
    <p class="summary-label">{{ label }}</p>
    <span class="summary-orb" />
  </article>
</template>

<style scoped>
.summary-card {
  min-height: 142px;
  padding: 20px 20px 18px 23px;
  overflow: hidden;
  transition: transform var(--transition-base), border-color var(--transition-base), box-shadow var(--transition-base);
}
.summary-card:hover {
  transform: translateY(-3px);
  border-color: color-mix(in srgb, var(--summary-accent) 52%, var(--color-border));
  box-shadow: var(--shadow-md);
}
.summary-line {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--summary-accent);
  box-shadow: 0 0 20px color-mix(in srgb, var(--summary-accent) 55%, transparent);
}
.summary-top {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.summary-eyebrow {
  color: var(--color-text-muted);
  font-size: 0.61rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.summary-icon {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  color: var(--summary-accent);
  border: 1px solid color-mix(in srgb, var(--summary-accent) 30%, transparent);
  border-radius: 11px;
  background: color-mix(in srgb, var(--summary-accent) 12%, transparent);
}
.summary-value {
  position: relative;
  z-index: 1;
  margin: 15px 0 2px;
  color: var(--color-text);
  font-size: clamp(1.75rem, 2.4vw, 2.25rem);
  font-weight: 700;
  letter-spacing: -0.045em;
  line-height: 1;
}
.summary-label {
  position: relative;
  z-index: 1;
  margin: 8px 0 0;
  color: var(--color-text-muted);
  font-size: 0.72rem;
  line-height: 1.35;
}
.summary-orb {
  position: absolute;
  right: -34px;
  bottom: -54px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: var(--summary-accent);
  filter: blur(48px);
  opacity: 0.08;
}
</style>
