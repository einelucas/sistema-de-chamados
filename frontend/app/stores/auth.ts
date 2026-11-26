import { defineStore } from 'pinia'
import type { User } from '~/types/user'
interface AuthState {user:User|null;initialized:boolean}
export const useAuthStore=defineStore('auth',{
  state:():AuthState=>({user:null,initialized:false}),
  getters:{
    isAuthenticated:state=>Boolean(state.user),
    isAdmin:state=>state.user?.role==='ADMIN',
    isAnalystOrAdmin:state=>state.user?.role==='ADMIN'||state.user?.role==='ANALYST',
  },
  actions:{
    setSession(user:User){validateSessionUser(user);useNuxtApp().$resetApi();this.user=user;useThemeStore().syncFromUser(user)},
    setUser(user:User){validateSessionUser(user);this.user=user;useThemeStore().syncFromUser(user)},
    expire(){
      useNuxtApp().$resetApi();this.user=null
      if(import.meta.client)void navigateTo('/login')
    },
    async logout(){
      try{await useNuxtApp().$api('/auth/logout',{method:'POST'})}
      catch{useToast().error('Não foi possível encerrar a sessão. Tente novamente.');return}
      this.expire()
    },
    async restoreSession(){
      if(this.initialized||!import.meta.client)return
      this.initialized=true
      window.sessionStorage.removeItem('central_token')
      try{this.setSession(await useNuxtApp().$api<User>('/auth/me'))}
      catch{this.user=null}
    },
  },
})
