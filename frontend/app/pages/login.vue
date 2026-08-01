<script setup lang="ts">
definePageMeta({ layout: 'auth', middleware: 'guest' })

const { login } = useAuth()
const route = useRoute()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function handleSubmit() {
  errorMessage.value = ''
  if (!email.value || !password.value) {
    errorMessage.value = 'Informe e-mail e senha.'
    return
  }

  loading.value = true
  try {
    await login(email.value, password.value)
    await navigateTo((route.query.redirect as string) || '/dashboard')
  } catch (error) {
    errorMessage.value = extractErrorMessage(error, 'E-mail ou senha inválidos.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-intro">
      <div class="intro-brand">
        <span class="brand-mark"><span class="brand-line" /><span class="brand-dot" /></span>
        <div>
          <strong>CENTRAL</strong>
          <span>SOLICITAÇÕES</span>
        </div>
      </div>

      <div class="intro-content">
        <span class="intro-kicker">Gestão interna centralizada</span>
        <h1>Solicitações organizadas.<br><em>Equipes em sintonia.</em></h1>
        <p>
          Acompanhe prioridades, responsáveis, prazos e histórico em um ambiente único,
          seguro e preparado para a rotina da sua equipe.
        </p>

        <div class="intro-features">
          <div class="feature">
            <span><UiIcon name="activity" :size="18" /></span>
            <div><strong>Visão operacional</strong><small>Indicadores e evolução em tempo real</small></div>
          </div>
          <div class="feature">
            <span><UiIcon name="shield" :size="18" /></span>
            <div><strong>Controle e segurança</strong><small>Acessos definidos por perfil</small></div>
          </div>
        </div>
      </div>

      <p class="intro-footer">Sistema interno · Central de Solicitações</p>
    </section>

    <section class="login-area">
      <div class="login-card">
        <div class="login-heading">
          <span class="access-icon"><UiIcon name="user" :size="23" /></span>
          <div>
            <span>Acesso seguro</span>
            <h2>Bem-vindo de volta</h2>
          </div>
        </div>
        <p class="login-description">Informe suas credenciais corporativas para continuar.</p>

        <form @submit.prevent="handleSubmit">
          <div class="form-field">
            <label for="email">E-mail</label>
            <div class="input-wrap">
              <UiIcon name="user" :size="18" />
              <input id="email" v-model="email" type="email" autocomplete="username" placeholder="seuemail@empresa.com">
            </div>
          </div>

          <div class="form-field">
            <label for="password">Senha</label>
            <div class="input-wrap">
              <UiIcon name="shield" :size="18" />
              <input id="password" v-model="password" type="password" autocomplete="current-password" placeholder="••••••••">
            </div>
          </div>

          <div v-if="errorMessage" class="login-error" role="alert">
            <UiIcon name="open" :size="17" />
            <span>{{ errorMessage }}</span>
          </div>

          <button class="btn btn-primary submit-button" type="submit" :disabled="loading">
            <span>{{ loading ? 'Validando acesso...' : 'Entrar no sistema' }}</span>
            <UiIcon v-if="!loading" name="arrowRight" :size="18" />
            <span v-else class="loading-dot" />
          </button>
        </form>

        <div class="security-note">
          <UiIcon name="shield" :size="15" />
          <span>Conexão protegida e acesso monitorado</span>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(430px, 0.95fr);
}
.login-intro {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 42px clamp(36px, 6vw, 92px) 34px;
  border-right: 1px solid var(--color-border);
  background: linear-gradient(135deg, rgba(var(--primary-rgb), 0.06), transparent 55%), var(--color-surface);
}
.intro-brand {
  display: flex;
  align-items: center;
  gap: 13px;
}
.brand-mark {
  position: relative;
  width: 46px;
  height: 46px;
  overflow: hidden;
  border: 1px solid var(--brand-mark-border);
  border-radius: 14px;
  background: var(--brand-mark-bg);
  box-shadow: 0 16px 36px rgba(var(--primary-rgb), 0.14);
}
.brand-line {
  position: absolute;
  left: 10px;
  top: 22px;
  width: 24px;
  height: 4px;
  border-radius: 99px;
  background: var(--color-primary);
  transform: rotate(-38deg);
  box-shadow: 0 -9px 0 var(--brand-secondary-line), 0 9px 0 var(--brand-accent-line);
}
.brand-dot {
  position: absolute;
  top: 7px;
  right: 7px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--color-accent);
  box-shadow: 0 0 12px var(--brand-accent-glow);
}
.intro-brand > div {
  display: flex;
  flex-direction: column;
}
.intro-brand strong {
  color: var(--color-primary);
  font-family: 'Aclonica', sans-serif;
  font-size: 1.05rem;
  font-weight: 400;
  letter-spacing: 0.07em;
}
.intro-brand > div span {
  margin-top: 4px;
  color: var(--color-text-soft);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.18em;
}
.intro-content {
  width: min(100%, 650px);
  margin: auto 0;
  padding: 70px 0;
}
.intro-kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--color-primary);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}
.intro-kicker::before {
  content: '';
  width: 30px;
  height: 1px;
  background: var(--color-primary);
}
.intro-content h1 {
  margin: 24px 0 22px;
  font-size: clamp(2.25rem, 4.1vw, 4.35rem);
  line-height: 1.08;
  letter-spacing: -0.055em;
}
.intro-content h1 em {
  color: var(--color-primary);
  font-style: normal;
}
.intro-content > p {
  max-width: 570px;
  margin-bottom: 0;
  color: var(--color-text-muted);
  font-size: clamp(0.92rem, 1.25vw, 1.05rem);
  line-height: 1.75;
}
.intro-features {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 42px;
}
.feature {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  background: var(--color-surface-soft);
}
.feature > span {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  color: var(--color-primary);
  border-radius: 10px;
  background: var(--color-primary-light);
}
.feature div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.feature strong {
  color: var(--color-text-soft);
  font-size: 0.72rem;
}
.feature small {
  color: var(--color-text-muted);
  font-size: 0.62rem;
  line-height: 1.35;
}
.intro-footer {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.65rem;
}
.login-area {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 40px clamp(28px, 6vw, 84px);
  background: rgba(237, 243, 249, 0.82);
}
.login-card {
  width: min(100%, 460px);
  padding: clamp(28px, 4vw, 42px);
  background: linear-gradient(155deg, rgba(var(--primary-rgb), 0.035), transparent 38%), var(--color-surface);
  border: 1px solid var(--color-border-strong);
  border-radius: 24px;
  box-shadow: 0 30px 80px rgba(15, 23, 42, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.9);
}
.login-heading {
  display: flex;
  align-items: center;
  gap: 14px;
}
.access-icon {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  color: var(--color-primary);
  border: 1px solid var(--color-primary-border);
  border-radius: 14px;
  background: var(--color-primary-light);
}
.login-heading > div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.login-heading span {
  color: var(--color-primary);
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.login-heading h2 {
  margin: 0;
  font-size: 1.45rem;
}
.login-description {
  margin: 18px 0 30px;
  color: var(--color-text-muted);
  font-size: 0.8rem;
  line-height: 1.55;
}
.input-wrap {
  position: relative;
}
.input-wrap > svg {
  position: absolute;
  left: 14px;
  top: 50%;
  z-index: 1;
  color: var(--placeholder);
  transform: translateY(-50%);
  pointer-events: none;
}
.input-wrap input {
  padding-left: 44px;
}
.input-wrap:focus-within > svg {
  color: var(--color-primary);
}
.login-error {
  display: flex;
  align-items: center;
  gap: 9px;
  margin: -2px 0 16px;
  padding: 11px 12px;
  color: var(--color-danger);
  background: var(--color-danger-light);
  border: 1px solid rgba(217, 54, 69, 0.24);
  border-radius: 10px;
  font-size: 0.72rem;
}
.submit-button {
  width: 100%;
  min-height: 48px;
  justify-content: space-between;
  margin-top: 4px;
  padding-inline: 18px;
}
.loading-dot {
  width: 15px;
  height: 15px;
  border: 2px solid rgba(255, 255, 255, 0.45);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
.security-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  margin-top: 24px;
  color: var(--placeholder);
  font-size: 0.62rem;
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 980px) {
  .login-page { grid-template-columns: 1fr; }
  .login-intro {
    min-height: auto;
    padding: 28px 28px 34px;
    border-right: 0;
    border-bottom: 1px solid var(--color-border);
  }
  .intro-content { padding: 54px 0 24px; }
  .intro-content h1 { font-size: clamp(2.1rem, 8vw, 3.7rem); }
  .intro-footer { display: none; }
  .login-area { min-height: auto; padding: 48px 22px 70px; }
}
@media (max-width: 600px) {
  .login-intro { padding: 24px 20px 28px; }
  .intro-features { grid-template-columns: 1fr; }
  .login-area { padding: 34px 14px 50px; }
  .login-card { padding: 26px 20px; border-radius: 18px; }
}
</style>
