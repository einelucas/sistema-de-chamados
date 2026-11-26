import type { User } from '~/types/user'
export function useAuth(){
  const auth=useAuthStore(),{$api}=useNuxtApp()
  async function login(email:string,password:string){
    const response=await $api<{user:User}>('/auth/login',{method:'POST',body:{email,password}})
    auth.setSession(response.user)
    return response.user
  }
  return {login,logout:()=>auth.logout(),user:computed(()=>auth.user),isAuthenticated:computed(()=>auth.isAuthenticated),isAdmin:computed(()=>auth.isAdmin),isAnalystOrAdmin:computed(()=>auth.isAnalystOrAdmin)}
}
