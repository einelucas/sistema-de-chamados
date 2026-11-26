/** Same-origin gateway. The browser never receives the Central JWT. */
const cookie = 'central_session'
const validPath = /^(auth|requests|users|dashboard|attachments|comments|sync)(?:\/[a-zA-Z0-9_-]+)*$/
export default defineEventHandler(async event => {
  const path = getRouterParam(event,'path') || ''
  if(!validPath.test(path))throw createError({statusCode:404,statusMessage:'Endpoint indisponível'})
  const method=getMethod(event)
  setResponseHeader(event,'Cache-Control','no-store')
  const config=useRuntimeConfig(event)
  const base=String(config.apiBase||config.public.apiBase).replace(/\/$/,'')
  const url=new URL(base)
  if(!['http:','https:'].includes(url.protocol)||url.username||url.password||url.search||url.hash)throw createError({statusCode:503,statusMessage:'API indisponível'})
  if(!['GET','HEAD','OPTIONS'].includes(method)){
    const origin=getRequestHeader(event,'origin')
    // Host is controlled by the browser, not by a page making a cross-site request.
    const expected=getRequestURL(event,{xForwardedHost:true,xForwardedProto:true}).origin
    if(origin!==expected)throw createError({statusCode:403,statusMessage:'Origem não autorizada'})
  }
  if(path==='auth/login'&&method==='POST'){
    try{
      const login=await $fetch<{access_token:string;user:unknown}>(base+'/auth/login',{method:'POST',body:await readBody(event),retry:0,timeout:15000,redirect:'error'})
      if(typeof login.access_token!=='string'||!login.user||typeof (login.user as {must_change_password?:unknown}).must_change_password!=='boolean')throw createError({statusCode:502,statusMessage:'Resposta de login inválida'})
      setCookie(event,cookie,login.access_token,{httpOnly:true,secure:getRequestURL(event,{xForwardedProto:true}).protocol==='https:',sameSite:'lax',path:'/',maxAge:3600})
      return {user:login.user}
    }catch(e){
      const error=e as {statusCode?:number;status?:number;data?:{detail?:string}}
      const status=error.statusCode??error.status??503
      throw createError({statusCode:status,statusMessage:status===401?'Credenciais inválidas':'Não foi possível iniciar a sessão',data:{detail:error.data?.detail}})
    }
  }
  if(path==='auth/change-password'&&method==='POST'){
    const token=getCookie(event,cookie)
    if(!token)throw createError({statusCode:401,statusMessage:'Sessão necessária'})
    const result=await $fetch<{access_token:string;user:unknown}>(base+'/auth/change-password',{method:'POST',headers:{authorization:'Bearer '+token},body:await readBody(event),retry:0,timeout:15000,redirect:'error'})
    if(typeof result.access_token!=='string'||!result.user||typeof (result.user as {must_change_password?:unknown}).must_change_password!=='boolean')throw createError({statusCode:502,statusMessage:'Resposta de autenticação inválida'})
    setCookie(event,cookie,result.access_token,{httpOnly:true,secure:getRequestURL(event,{xForwardedProto:true}).protocol==='https:',sameSite:'lax',path:'/',maxAge:3600})
    return {user:result.user}
  }
  if(path==='auth/logout'&&method==='POST'){
    deleteCookie(event,cookie,{path:'/',httpOnly:true,sameSite:'lax'})
    return {ok:true}
  }
  const token=getCookie(event,cookie)
  if(!token)throw createError({statusCode:401,statusMessage:'Sessão necessária'})
  const headers:Record<string,string>={authorization:'Bearer '+token,cookie:''}
  for(const name of ['content-type','accept','last-event-id']){
    const value=getRequestHeader(event,name);if(value)headers[name]=value
  }
  return proxyRequest(event,base+'/'+path+getRequestURL(event).search,{headers,fetchOptions:{redirect:'manual'}})
})
