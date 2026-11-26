import asyncio,json,time
from fastapi import APIRouter,Depends,Header,HTTPException,Request,Response
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.database.session import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User
from app.services.support_sync import revision
router=APIRouter(prefix="/sync",tags=["Sincronização"])

@router.get("/version")
def get_version(response:Response,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    response.headers["Cache-Control"]="no-store"
    return {"revision":revision(db,user)}

def snapshot(token):
    claims=decode_access_token(token)
    if not claims:return None
    try:uid=int(claims["sub"])
    except (TypeError,ValueError,KeyError):return None
    with SessionLocal() as db:
        user=db.get(User,uid)
        if not user or not user.is_active or user.integration_identity or user.must_change_password or claims.get('sv',1)!=user.session_version:return None
        return revision(db,user)

@router.get("/events/stream")
async def stream(request:Request,authorization:str|None=Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):raise HTTPException(401,"Sessão necessária")
    token=authorization.split(" ",1)[1]
    initial=await run_in_threadpool(snapshot,token)
    if initial is None:raise HTTPException(401,"Sessão inválida")
    async def events():
        value=initial
        yield "retry: 2000\n\nevent: ready\ndata: "+json.dumps({"revision":value})+"\n\n"
        deadline=time.monotonic()+25
        while time.monotonic()<deadline and not await request.is_disconnected():
            await asyncio.sleep(3)
            try:next_value=await run_in_threadpool(snapshot,token)
            except Exception:break
            if next_value is None:
                yield "event: revoked\ndata: {}\n\n";break
            if value!=next_value:
                value=next_value
                yield "event: change\ndata: "+json.dumps({"revision":value})+"\n\n"
            else:yield ": heartbeat\n\n"
    return StreamingResponse(events(),media_type="text/event-stream",headers={"Cache-Control":"no-cache, no-transform","X-Accel-Buffering":"no"})
