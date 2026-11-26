import { spawn } from 'node:child_process'
import { createServer } from 'node:http'
import assert from 'node:assert/strict'
import { once } from 'node:events'
const user={id:1,name:'Test',email:'test@example.com',role:'ADMIN',is_active:true,must_change_password:true,theme_preference:'light',created_at:'2026-01-01T00:00:00Z',updated_at:'2026-01-01T00:00:00Z'}
const upstream=createServer((req,res)=>{
  res.setHeader('content-type','application/json')
  if(req.url==='/api/v1/auth/login'&&req.method==='POST'){
    req.resume();res.end(JSON.stringify({access_token:'mock-session-token',user}))
  }else if(req.url==='/api/v1/auth/me'&&req.headers.authorization==='Bearer mock-session-token'){
    res.end(JSON.stringify(user))
  }else{res.statusCode=401;res.end(JSON.stringify({detail:'Unauthorized'}))}
})
upstream.listen(0,'127.0.0.1');await once(upstream,'listening')
const port=43123,origin='http://127.0.0.1:'+port
const server=spawn(process.execPath,['.output/server/index.mjs'],{env:{...process.env,HOST:'127.0.0.1',PORT:String(port),NUXT_API_BASE:'http://127.0.0.1:'+upstream.address().port+'/api/v1'},stdio:'inherit'})
try{
  let ready=false
  for(let i=0;i<80;i++){try{await fetch(origin);ready=true;break}catch{await new Promise(r=>setTimeout(r,250))}}
  assert.ok(ready,'Nitro server did not start')
  const denied=await fetch(origin+'/api/auth/me')
  assert.equal(denied.status,401,'API route must not return SPA HTML')
  assert.match(denied.headers.get('content-type')??'',/json/)
  const login=await fetch(origin+'/api/auth/login',{method:'POST',headers:{origin,'content-type':'application/json'},body:JSON.stringify({email:'test@example.com',password:'test-fixture'})})
  assert.equal(login.status,200)
  const data=await login.json()
  assert.equal(data.user.must_change_password,true)
  assert.equal(data.access_token,undefined)
  const cookie=login.headers.get('set-cookie')
  assert.match(cookie??'',/HttpOnly/i)
  const me=await fetch(origin+'/api/auth/me',{headers:{cookie:cookie.split(';')[0]}})
  assert.equal(me.status,200);assert.equal((await me.json()).id,1)
  console.log('Gateway login, session and API routing smoke passed')
}finally{server.kill();upstream.close()}
