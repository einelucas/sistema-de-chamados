export function useSilentRefresh(refresh:()=>Promise<void>, milliseconds=10000){
  let timer: ReturnType<typeof setTimeout>|undefined, active=false, pending=false
  async function tick(){
    if(!active||pending||document.visibilityState!=='visible'||!navigator.onLine)return
    pending=true
    try {await refresh()} finally {pending=false}
  }
  function schedule(){if(!active)return;timer=setTimeout(async()=>{await tick();schedule()},milliseconds)}
  function visible(){void tick()}
  onMounted(()=>{active=true;schedule();window.addEventListener('online',visible);document.addEventListener('visibilitychange',visible)})
  onBeforeUnmount(()=>{active=false;clearTimeout(timer);window.removeEventListener('online',visible);document.removeEventListener('visibilitychange',visible)})
}
