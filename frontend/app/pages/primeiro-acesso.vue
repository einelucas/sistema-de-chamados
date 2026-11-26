<script setup lang="ts">
definePageMeta({layout:'auth',middleware:'auth'})
const auth=useAuthStore(),{$api}=useNuxtApp()
const current=ref(''),password=ref(''),confirmation=ref(''),error=ref(''),busy=ref(false)
async function save(){
  if(busy.value)return
  error.value=''
  if(password.value!==confirmation.value){error.value='As senhas não coincidem.';return}
  const size=new TextEncoder().encode(password.value).length
  if(size<12||size>72){error.value='Use uma senha de 12 a 72 bytes.';return}
  busy.value=true
  try{
    const result=await $api<{user:import('~/types/user').User}>('/auth/change-password',{method:'POST',body:{current_password:current.value,new_password:password.value}})
    auth.setSession(validateSessionUser(result?.user))
    current.value='';password.value='';confirmation.value=''
    await navigateTo('/dashboard')
  }catch(e){error.value=extractErrorMessage(e,'Não foi possível alterar a senha.')}
  finally{busy.value=false}
}
</script>
<template>
  <main class="first-access">
    <section class="card first-access-card">
      <img src="~/assets/brand/logo.png" class="nexotiva-logo" alt="Nexotiva">
      <h1>Primeiro acesso</h1>
      <p>Defina sua senha pessoal antes de acessar a Central de Chamados.</p>
      <form @submit.prevent="save">
        <VTextField v-model="current" label="Senha temporária" type="password" autocomplete="current-password" required/><VTextField v-model="password" label="Nova senha" type="password" autocomplete="new-password" minlength="12" required/><VTextField v-model="confirmation" label="Confirme a nova senha" type="password" autocomplete="new-password" minlength="12" required/><p class="hint">Use pelo menos 12 caracteres e uma senha diferente da temporária.</p>
        <p v-if="error" role="alert" class="error">{{error}}</p>
        <VBtn type="submit" class="hub-action-button" color="primary" variant="flat" :disabled="busy">{{busy?'Salvando...':'Definir senha e entrar'}}</VBtn>
        <VBtn type="button" class="hub-action-button" color="secondary" variant="outlined" :disabled="busy" @click="auth.logout()">Sair</VBtn>
      </form>
    </section>
  </main>
</template>
<style scoped>
.first-access{min-height:100dvh;display:grid;place-items:center;padding:20px}.first-access-card{width:min(100%,440px);padding:32px}.first-access-card h1{margin:16px 0 8px;font-size:1.5rem}.first-access-card p{color:var(--color-text-muted);font-size:.85rem}.first-access-card form{display:grid;gap:10px;margin-top:24px}.first-access-card label{font-weight:700;font-size:.8rem}.first-access-card .error{color:var(--color-danger)}.hint{margin:0 0 8px}
</style>
