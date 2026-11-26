export default defineNuxtPlugin(nuxt=>{
  const auth=useAuthStore()
  const api=nuxt.$api as <T>(path:string,options?:{force?:boolean})=>Promise<T>
  const clear=nuxt.$clearApi as ()=>void
  let fallback:ReturnType<typeof setTimeout>|undefined
  let source:EventSource|null=null,retry:ReturnType<typeof setTimeout>|undefined,revision='',attempts=0,identity:number|null=null
  const status=useState('central-sync-status',()=> 'idle')
  function stop(){source?.close();source=null;clearTimeout(retry)}
  function refresh(){clear();window.dispatchEvent(new Event('central:sync'))}
  function connect(){
    if(!auth.user||auth.user.must_change_password||source||document.visibilityState!=='visible'||!navigator.onLine)return
    status.value='connecting'
    const stream=new EventSource('/api/sync/events/stream')
    source=stream
    const received=(event:MessageEvent)=>{
      if(source!==stream)return
      try{const next=JSON.parse(event.data).revision as string;status.value='connected';attempts=0;if(next!==revision){const previous=revision;revision=next;refresh();if(previous&&auth.isAnalystOrAdmin)nuxt.runWithContext(()=>useToast().success('Novas atualizações na fila de atendimento.'))}}catch{}
    }
    stream.addEventListener('ready',received);stream.addEventListener('change',received)
    stream.addEventListener('revoked',()=>{if(source===stream)nuxt.runWithContext(()=>auth.expire())})
    stream.onerror=()=>{if(source!==stream)return;stop();status.value=navigator.onLine?'reconnecting':'offline';retry=setTimeout(connect,Math.min(30000,2000*2**Math.min(attempts++,4)))}
  }
  function focus(){if(document.visibilityState==='hidden'){stop();return}if(navigator.onLine){refresh();connect()}}
  watch(()=>auth.user&&!auth.user.must_change_password?auth.user.id:null,id=>{if(id===identity)return;identity=id;stop();revision='';status.value='idle';connect()},{immediate:true})
  window.addEventListener('online',focus);window.addEventListener('focus',focus)
  window.addEventListener('offline',()=>{stop();status.value='offline'})
  document.addEventListener('visibilitychange',focus)
  window.addEventListener('central:changed',refresh)
  // No component lifecycle hooks in plugins. Reconcile versions even when SSE
  // is unavailable and let authorized checks drain the outbox.
  async function poll(){
    const current=auth.user&&!auth.user.must_change_password?auth.user.id:null
    if(current&&navigator.onLine&&document.visibilityState==='visible'){
      try{const v=await api<{revision:string}>('/sync/version',{force:true});if(auth.user?.id===current&&v.revision!==revision){revision=v.revision;refresh()}}catch{}
    }
    if(auth.user)fallback=setTimeout(poll,15000)
  }
  watch(()=>auth.user?.id,()=>{clearTimeout(fallback);if(auth.user)fallback=setTimeout(poll,15000)},{immediate:true})
  if(import.meta.hot)import.meta.hot.dispose(()=>{stop();clearTimeout(fallback)})
})
