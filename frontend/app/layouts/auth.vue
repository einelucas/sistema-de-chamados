<script setup lang="ts">
// Layout exclusivo da autenticação. O acesso permanece claro independentemente
// da preferência salva, e o tema do usuário é reaplicado após o login.
</script>

<template>
  <div class="auth-shell">
    <div class="auth-glow auth-glow-primary" />
    <div class="auth-glow auth-glow-accent" />
    <slot />
    <UiToastContainer />
  </div>
</template>

<style scoped>
.auth-shell {
  --color-bg: #f4f7fb;
  --color-bg-soft: #edf3f9;
  --color-surface: #ffffff;
  --color-surface-soft: #f8fafc;
  --color-surface-elevated: #ffffff;
  --color-border: #dce5ef;
  --color-border-strong: #c5d2df;
  --color-text: #0f172a;
  --color-text-soft: #334155;
  --color-text-muted: #64748b;
  --color-primary: #2563eb;
  --color-primary-dark: #1d4ed8;
  --color-primary-light: rgba(37, 99, 235, 0.10);
  --color-primary-glow: rgba(37, 99, 235, 0.18);
  --color-primary-border: rgba(37, 99, 235, 0.34);
  --primary-rgb: 37, 99, 235;
  --color-accent: #c58a18;
  --accent-rgb: 197, 138, 24;
  --color-danger: #d93645;
  --color-danger-light: rgba(217, 54, 69, 0.10);
  --surface-translucent: rgba(255, 255, 255, 0.72);
  --button-primary-start: #3b82f6;
  --button-primary-end: #1d4ed8;
  --button-primary-text: #ffffff;
  --placeholder: #94a3b8;
  --focus-ring: rgba(37, 99, 235, 0.17);
  --shadow-primary: 0 14px 34px rgba(37, 99, 235, 0.22);
  --input-hover-border: #94a3b8;
  --input-focus-bg: #ffffff;
  --input-disabled-bg: #eef2f7;
  --brand-mark-bg: linear-gradient(145deg, rgba(37, 99, 235, 0.16), rgba(37, 99, 235, 0.035));
  --brand-mark-border: rgba(37, 99, 235, 0.30);
  --brand-secondary-line: rgba(37, 99, 235, 0.38);
  --brand-accent-line: rgba(197, 138, 24, 0.82);
  --brand-accent-glow: rgba(197, 138, 24, 0.38);

  position: relative;
  min-height: 100vh;
  overflow: hidden;
  color: var(--color-text);
  color-scheme: light;
  background:
    linear-gradient(rgba(37, 99, 235, 0.028) 1px, transparent 1px),
    linear-gradient(90deg, rgba(37, 99, 235, 0.028) 1px, transparent 1px),
    var(--color-bg);
  background-size: 42px 42px;
}
.auth-glow {
  position: fixed;
  width: 36rem;
  height: 36rem;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
  opacity: 0.12;
}
.auth-glow-primary {
  top: -18rem;
  right: -10rem;
  background: var(--color-primary);
}
.auth-glow-accent {
  bottom: -24rem;
  left: -12rem;
  background: var(--color-accent);
  opacity: 0.055;
}
</style>
