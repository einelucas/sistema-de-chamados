import axios from 'axios'
type Options={method?:'GET'|'POST'|'PUT'|'PATCH'|'DELETE';body?:unknown;query?:Record<string,unknown>;responseType?:'json'|'blob';force?:boolean;signal?:AbortSignal}
type Entry={expires:number;value:unknown}
export function createCentralApi(onUnauthorized:()=>void){
  const http=axios.create({baseURL:'/api',timeout:15000,withCredentials:true})
  const entries=new Map<string,Entry>(), pending=new Map<string,Promise<unknown>>()
  let epoch=0, controller=new AbortController()
  function clear(){entries.clear();pending.clear()}
  function reset(){epoch++;controller.abort();controller=new AbortController();clear()}
  async function api<T>(path:string,options:Options={}):Promise<T>{
    if(!/^\/[a-zA-Z0-9_/-]+$/.test(path)||path.includes('//'))throw new Error('Endpoint inválido')
    const method=options.method??'GET', current=epoch
    const query=Object.fromEntries(Object.entries(options.query??{}).filter(([,v])=>v!==undefined&&v!==null&&v!=='').sort(([a],[b])=>a.localeCompare(b)))
    const key=path+JSON.stringify(query)
    const dedup=method==='GET'&&!options.signal&&!options.responseType&&!path.startsWith('/auth/')
    // Cache only options/catalog; ticket records are always revalidated.
    const ttl=path==='/requests/contexts'?30_000:0
    if(dedup&&!options.force&&ttl){const hit=entries.get(key);if(hit&&hit.expires>Date.now())return hit.value as T}
    if(dedup&&pending.has(key))return pending.get(key) as Promise<T>
    const signal=options.signal?AbortSignal.any([controller.signal,options.signal]):controller.signal
    const load=async()=>{
      for(let i=0;;i++){
        try{
          const res=await http.request<T>({url:path,method,data:options.body,params:query,responseType:options.responseType??'json',signal})
          if(current!==epoch||signal.aborted)throw new Error('Requisição cancelada')
          if(method!=='GET'){clear();if(!path.startsWith('/auth/'))window.dispatchEvent(new Event('central:changed'))}
          return res.data
        }catch(e){
          if(signal.aborted||current!==epoch||!axios.isAxiosError(e))throw e
          const status=e.response?.status??0
          if(method==='GET'&&i===0&&[0,408,500,502,503,504].includes(status))continue
          if(status===401&&!path.startsWith('/auth/'))onUnauthorized()
          if([401,403,404].includes(status))clear()
          throw Object.assign(new Error(typeof e.response?.data?.detail==='string'?e.response.data.detail:'Não foi possível concluir a operação.'),{statusCode:status,data:e.response?.data})
        }
      }
    }
    if(!dedup)return load()
    const request=load().then(value=>{if(ttl&&pending.get(key)===request&&current===epoch){entries.set(key,{expires:Date.now()+ttl,value});while(entries.size>100)entries.delete(entries.keys().next().value!)}return value}).finally(()=>{if(pending.get(key)===request)pending.delete(key)})
    pending.set(key,request)
    return request
  }
  return {api,reset,clear}
}
