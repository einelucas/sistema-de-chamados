<script setup lang="ts">
definePageMeta({ layout: 'auth', middleware: 'guest' })

const { login } = useAuth()
const route = useRoute()

const email = ref('')
const password = ref('')
const loading = ref(false)
const showPassword=ref(false)
const errorMessage = ref('')

async function handleSubmit() {
  if(loading.value)return
  errorMessage.value = ''
  if (!email.value || !password.value) {
    errorMessage.value = 'Informe e-mail e senha.'
    return
  }

  loading.value = true
  try {
    const user=await login(email.value,password.value)
    const redirect=typeof route.query.redirect==='string'&&route.query.redirect.startsWith('/')&&!route.query.redirect.startsWith('//')?route.query.redirect:'/dashboard'
    await navigateTo(user.must_change_password?'/primeiro-acesso':redirect)
  } catch (error) {
    errorMessage.value = extractErrorMessage(error, 'E-mail ou senha inválidos.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <VCard class="central-login-card" variant="outlined">
    <div class="login-brand"><img src="/brand/logo.png" alt="Nexotiva"><span>Central de Chamados</span></div>
    <h1>Acesse sua conta</h1>
    <VForm @submit.prevent="handleSubmit">
      <VAlert v-if="errorMessage" type="error" variant="tonal" class="mb-4" role="alert">{{errorMessage}}</VAlert>
      <VTextField v-model="email" label="E-mail" type="email" autocomplete="username" required class="mb-4" :disabled="loading"/>
      <VTextField v-model="password" label="Senha" :type="showPassword?'text':'password'" autocomplete="current-password" required class="mb-5" :disabled="loading">
        <template #append-inner><VBtn icon variant="text" size="small" :aria-label="showPassword?'Ocultar senha':'Mostrar senha'" @click="showPassword=!showPassword"><UiIcon :name="showPassword?'eyeOff':'eye'" :size="19"/></VBtn></template>
      </VTextField>
      <VBtn type="submit" block color="primary" variant="flat" class="hub-action-button" :loading="loading" :disabled="loading">Entrar</VBtn>
    </VForm>
  </VCard>
</template>
<style scoped>
.central-login-card{width:min(100%,420px);padding:32px;background:#fff;border-color:#e2e8f0;border-radius:12px!important;box-shadow:0 8px 30px #0f172a08!important}
.login-brand{display:flex;flex-direction:column;align-items:center;gap:10px;margin-bottom:28px;color:#64748b;font-size:13px;font-weight:600}.login-brand img{width:64px;height:64px;object-fit:contain}
h1{font-size:22px;letter-spacing:-.03em;margin:0 0 24px;font-weight:750;color:#1f2937}
@media(max-width:480px){.central-login-card{padding:24px}}
</style>
