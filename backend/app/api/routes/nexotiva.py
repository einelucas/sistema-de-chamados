"""Server-to-server API; never expose the integration token to a browser."""
import hashlib
import base64
import binascii
import json
from pathlib import Path
from uuid import uuid4
import secrets
from typing import Annotated, Literal
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_db
from app.core.config import settings
from app.core.security import hash_password
from app.models.enums import HistoryAction, RequestCategory, RequestPriority, RequestStatus, UserRole
from app.models.history import RequestHistory
from app.models.comment import Comment
from app.models.attachment import Attachment
from app.models.nexotiva_ticket import NexotivaTicket
from app.models.request import Request
from app.models.user import User

def integration_auth(authorization: str | None = Header(default=None)):
    key = settings.NEXOTIVA_INTEGRATION_TOKEN
    if len(key) < 32:
        raise HTTPException(503, "Integração não configurada")
    if not secrets.compare_digest((authorization or "").encode(), ("Bearer " + key).encode()):
        raise HTTPException(401, "Integração não autorizada")

router = APIRouter(prefix="/integrations/nexotiva/tickets", tags=["Nexotiva"], dependencies=[Depends(integration_auth)])

class TicketInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    company_id: UUID | Literal["account"]
    company_name: str = Field(min_length=1, max_length=150)
    user_id: UUID
    user_name: str = Field(min_length=1, max_length=150)
    user_email: str = Field(min_length=3, max_length=254)
    module_slug: str = Field(min_length=1, max_length=100)
    module_name: str = Field(min_length=1, max_length=120)
    client_request_id: UUID
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3, max_length=8000)
    category: RequestCategory
    priority: RequestPriority = RequestPriority.MEDIA

def scoped(company_id: str, user_id: str):
    return (select(Request, NexotivaTicket)
        .join(NexotivaTicket, NexotivaTicket.request_id == Request.id)
        .where(NexotivaTicket.company_id == company_id, NexotivaTicket.user_id == user_id,
               Request.is_deleted.is_(False)))

def serialize(row):
    r, link = row
    return {"id": r.id, "title": r.title, "description": r.description, "status": r.status.value,
            "priority": r.priority.value, "category": r.category.value, "module_name": link.module_name,
            "created_at": r.created_at, "updated_at": r.updated_at}

@router.get("")
def list_tickets(response: Response, company_id: UUID | Literal["account"], user_id: UUID,
                 page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50),
                 search: str = Query("", max_length=200), status: RequestStatus | None = None,
                 priority: RequestPriority | None = None, db: Session = Depends(get_db)):
    response.headers["Cache-Control"] = "no-store"
    base = scoped(str(company_id), str(user_id))
    scope = base.subquery()
    counts = dict(db.execute(select(scope.c.status, func.count()).group_by(scope.c.status)).all())
    stmt = base
    if search:
        stmt = stmt.where(or_(Request.title.ilike("%" + search + "%"), Request.description.ilike("%" + search + "%")))
    if status:
        stmt = stmt.where(Request.status == status)
    if priority:
        stmt = stmt.where(Request.priority == priority)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.execute(stmt.order_by(Request.created_at.desc(), Request.id.desc()).offset((page-1)*page_size).limit(page_size)).all()
    return {"items": [serialize(r) for r in rows], "total": total, "page": page, "page_size": page_size,
            "summary": {s.value: counts.get(s, 0) for s in RequestStatus}}

@router.get("/{ticket_id}")
def get_ticket(ticket_id: int, response: Response, company_id: UUID | Literal["account"], user_id: UUID, db: Session = Depends(get_db)):
    response.headers["Cache-Control"] = "no-store"
    row = db.execute(scoped(str(company_id), str(user_id)).where(Request.id == ticket_id)).one_or_none()
    if row is None:
        raise HTTPException(404, "Chamado não encontrado")
    return serialize(row)

def fingerprint(body):
    original=body.model_dump(mode="json",include={"title","description","category","priority","module_slug"})
    return hashlib.sha256(json.dumps(original,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def replay(row, body):
    r, link = row
    if r.is_deleted:
        raise HTTPException(409, "Chamado anterior arquivado")
    if link.payload_hash and link.payload_hash != fingerprint(body):
        raise HTTPException(409, "Identificador já utilizado com dados diferentes")
    if not link.payload_hash and (r.title, r.description, r.category, link.module_slug) != (body.title, body.description, body.category, body.module_slug):
        raise HTTPException(409, "Identificador já utilizado com dados diferentes")
    return serialize(row)

def ticket_or_404(db, cid, uid, ticket_id):
    row=db.execute(scoped(str(cid),str(uid)).where(Request.id==ticket_id)).one_or_none()
    if row is None: raise HTTPException(404,"Chamado não encontrado")
    return row

def public_comment(c, requester_id):
    return {"id":c.id,"content":c.content,"author":"customer" if c.author_id==requester_id else "support",
            "created_at":c.created_at,"updated_at":c.updated_at}

class ReplyInput(BaseModel):
    model_config=ConfigDict(extra="forbid",str_strip_whitespace=True)
    content:str=Field(min_length=1,max_length=4000)
    client_request_id:UUID

@router.get("/{ticket_id}/comments")
def get_replies(ticket_id:int,response:Response,company_id:UUID|Literal["account"],user_id:UUID,db:Session=Depends(get_db)):
    response.headers["Cache-Control"]="no-store"
    r,_=ticket_or_404(db,company_id,user_id,ticket_id)
    rows=db.scalars(select(Comment).where(Comment.request_id==r.id,Comment.public_reply.is_(True)).order_by(Comment.created_at,Comment.id))
    return [public_comment(c,r.requester_id) for c in rows]

@router.post("/{ticket_id}/comments",status_code=201)
def post_reply(ticket_id:int,body:ReplyInput,response:Response,company_id:UUID|Literal["account"],user_id:UUID,db:Session=Depends(get_db)):
    response.headers["Cache-Control"]="no-store"
    r,_=ticket_or_404(db,company_id,user_id,ticket_id)
    nonce=str(body.client_request_id)
    def existing():
        return db.scalar(select(Comment).where(Comment.request_id==r.id,Comment.client_request_id==nonce))
    def replay_comment(c):
        if c.author_id!=r.requester_id or c.content!=body.content or not c.public_reply:
            raise HTTPException(409,"Identificador já utilizado")
        return public_comment(c,r.requester_id)
    old=existing()
    if old:return replay_comment(old)
    if r.status in (RequestStatus.CONCLUIDA,RequestStatus.CANCELADA):
        raise HTTPException(409,"Chamado encerrado")
    try:
        c=Comment(request_id=r.id,author_id=r.requester_id,content=body.content,public_reply=True,client_request_id=nonce)
        db.add(c)
        db.add(RequestHistory(request_id=r.id,user_id=r.requester_id,action=HistoryAction.COMENTARIO_ADICIONADO))
        db.commit()
    except IntegrityError:
        db.rollback()
        old=existing()
        if old:return replay_comment(old)
        raise
    return public_comment(c,r.requester_id)

MAX_SHARED_BYTES=3*1024*1024

class SharedFileInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    filename:str=Field(min_length=1,max_length=255)
    content_base64:str=Field(min_length=1,max_length=4*((MAX_SHARED_BYTES+2)//3))
    client_request_id:UUID

def file_info(row):
    return {"id":row.id,"filename":row.original_filename,"size_bytes":row.size_bytes,"created_at":row.created_at}

@router.get("/{ticket_id}/attachments")
def list_shared_files(ticket_id:int,response:Response,company_id:UUID|Literal["account"],user_id:UUID,db:Session=Depends(get_db)):
    response.headers["Cache-Control"]="no-store"
    r,_=ticket_or_404(db,company_id,user_id,ticket_id)
    return [file_info(a) for a in db.scalars(select(Attachment).where(Attachment.request_id==r.id,Attachment.shared_with_customer.is_(True),Attachment.file_content.is_not(None)).order_by(Attachment.created_at,Attachment.id))]

@router.get("/{ticket_id}/attachments/{attachment_id}")
def download_shared_file(ticket_id:int,attachment_id:int,response:Response,company_id:UUID|Literal["account"],user_id:UUID,db:Session=Depends(get_db)):
    response.headers["Cache-Control"]="no-store"
    r,_=ticket_or_404(db,company_id,user_id,ticket_id)
    a=db.scalar(select(Attachment).where(Attachment.request_id==r.id,Attachment.id==attachment_id,Attachment.shared_with_customer.is_(True)))
    if not a or a.file_content is None:raise HTTPException(404,"Anexo não encontrado")
    return {**file_info(a),"content_base64":base64.b64encode(a.file_content).decode("ascii")}

@router.post("/{ticket_id}/attachments",status_code=201)
def upload_shared_file(ticket_id:int,body:SharedFileInput,response:Response,company_id:UUID|Literal["account"],user_id:UUID,db:Session=Depends(get_db)):
    response.headers["Cache-Control"]="no-store"
    r,_=ticket_or_404(db,company_id,user_id,ticket_id)
    name=body.filename.replace("\\\\","/").rsplit("/",1)[-1]
    extension=Path(name).suffix.lower()
    if extension not in settings.allowed_upload_extensions_list or any(ord(ch)<32 for ch in name):
        raise HTTPException(422,"Arquivo inválido")
    try: data=base64.b64decode(body.content_base64,validate=True)
    except (ValueError,binascii.Error):raise HTTPException(422,"Arquivo inválido")
    if not data or len(data)>min(settings.MAX_UPLOAD_SIZE,MAX_SHARED_BYTES):raise HTTPException(422,"Arquivo excede o limite")
    nonce=str(body.client_request_id)
    def existing():
        return db.scalar(select(Attachment).where(Attachment.request_id==r.id,Attachment.client_request_id==nonce))
    def replay_file(a):
        if a.uploaded_by_id!=r.requester_id or a.original_filename!=name or a.file_content!=data or not a.shared_with_customer:raise HTTPException(409,"Identificador já utilizado")
        return file_info(a)
    old=existing()
    if old:return replay_file(old)
    if r.status in (RequestStatus.CONCLUIDA,RequestStatus.CANCELADA):raise HTTPException(409,"Chamado encerrado")
    try:
        a=Attachment(request_id=r.id,uploaded_by_id=r.requester_id,original_filename=name,stored_filename=uuid4().hex+extension,content_type="application/octet-stream",size_bytes=len(data),file_content=data,shared_with_customer=True,client_request_id=nonce)
        db.add(a)
        db.add(RequestHistory(request_id=r.id,user_id=r.requester_id,action=HistoryAction.ANEXO_ADICIONADO,new_value=name))
        db.commit()
    except IntegrityError:
        db.rollback()
        old=existing()
        if old:return replay_file(old)
        raise
    return file_info(a)

@router.post("", status_code=201)
def create_ticket(body: TicketInput, response: Response, db: Session = Depends(get_db)):
    response.headers["Cache-Control"] = "no-store"
    cid, uid, nonce = str(body.company_id), str(body.user_id), str(body.client_request_id)
    def existing():
        return db.execute(select(Request,NexotivaTicket).join(NexotivaTicket,NexotivaTicket.request_id==Request.id).where(NexotivaTicket.company_id==cid,NexotivaTicket.user_id==uid,NexotivaTicket.client_request_id==nonce)).one_or_none()
    old = existing()
    if old:
        return replay(old, body)
    # A disabled shadow identity allows the existing admin UI to show the requester
    # without granting Central credentials to a Nexotiva customer.
    digest = hashlib.sha256((cid + ":" + uid).encode()).hexdigest()
    email = "nexotiva-" + digest + "@integration.example.com"
    actor = db.scalar(select(User).where(User.email == email))
    if actor is None:
        try:
            with db.begin_nested():
                actor = User(name=(body.company_name + " · " + body.user_name)[:150], email=email,
                             hashed_password=hash_password(secrets.token_urlsafe(32)), role=UserRole.USER, is_active=False, integration_identity=True)
                db.add(actor)
                db.flush()
        except IntegrityError:
            actor = db.scalar(select(User).where(User.email == email))
    if actor is None or actor.is_active or actor.role != UserRole.USER or not actor.integration_identity:
        raise HTTPException(409, "Identidade de integração incompatível")
    try:
        r = Request(title=body.title, description=body.description, category=body.category,
                    priority=body.priority, status=RequestStatus.ABERTA, requester_id=actor.id)
        db.add(r)
        db.flush()
        link = NexotivaTicket(request_id=r.id, company_id=cid, company_name=body.company_name,
                             user_id=uid, user_name=body.user_name, user_email=body.user_email,
                             module_slug=body.module_slug, module_name=body.module_name, client_request_id=nonce, payload_hash=fingerprint(body))
        db.add(link)
        db.add(RequestHistory(request_id=r.id, user_id=actor.id, action=HistoryAction.CRIACAO, new_value=r.title))
        db.commit()
    except IntegrityError:
        db.rollback()
        old = existing()
        if old:
            return serialize(old)
        raise
    return serialize((r, link))
