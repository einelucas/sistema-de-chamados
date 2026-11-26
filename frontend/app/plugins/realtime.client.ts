export default defineNuxtPlugin(nuxt=>{
  const auth=useAuthStore()
  let source:EventSource|null=null,retry:ReturnType<typeof setTimeout>|undefined,revision='',attempts=0,identity:number|null=null
  const status=useState('central-sync-status',()=> 'idle')
  function stop(){source?.close();source=null;clearTimeout(retry)}
  function refresh(){nuxt.$clearApi();window.dispatchEvent(new Event('central:sync'))}
  function connect(){
    if(!auth.user||source||document.visibilityState!=='visible'||!navigator.onLine)return
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
  watch(()=>auth.user?.id??null,id=>{if(id===identity)return;identity=id;stop();revision='';status.value='idle';connect()},{immediate:true})
  window.addEventListener('online',focus);window.addEventListener('focus',focus)
  window.addEventListener('offline',()=>{stop();status.value='offline'})
  document.addEventListener('visibilitychange',focus)
  window.addEventListener('central:changed',refresh)
  // Authorized version checks also drain the persisted webhook outbox on serverless.
  useSilentRefresh(async()=>{if(auth.user){try{const v=await nuxt.$api<{revision:string}>('/sync/version',{force:true});if(v.revision!==revision){revision=v.revision;refresh()}}catch{}}},15000)
})
