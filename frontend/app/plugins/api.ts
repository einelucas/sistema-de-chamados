import { createCentralApi } from '../services/api'
export default defineNuxtPlugin(()=>{
  const auth=useAuthStore()
  const transport=createCentralApi(()=>auth.expire())
  return {provide:{api:transport.api,resetApi:transport.reset,clearApi:transport.clear}}
})
