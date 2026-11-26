"""Revisions and webhook outbox are persisted in the same transaction as the data."""
from datetime import datetime,timezone
from uuid import uuid4
from sqlalchemy import event,select,inspect
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from app.models.request import Request
from app.models.comment import Comment
from app.models.attachment import Attachment
from app.models.nexotiva_ticket import NexotivaTicket
from app.models.support_sync import SupportRevision,SupportOutbox
from app.models.enums import UserRole

@event.listens_for(Session,"after_flush")
def record_changes(db,_):
    changed={}
    old_owners=set()
    for obj in list(db.new)+list(db.dirty)+list(db.deleted):
        if obj in db.dirty and not db.is_modified(obj,include_collections=False):continue
        if isinstance(obj,Request):
            if obj.id is None:continue
            changed.setdefault(obj.id,set()).add("ticket")
            old_owners.update(x for x in inspect(obj).attrs.assignee_id.history.deleted if x is not None)
        elif isinstance(obj,Comment):
            changed.setdefault(obj.request_id,set()).add("reply" if obj.public_reply else "internal")
        elif isinstance(obj,Attachment):
            changed.setdefault(obj.request_id,set()).add("attachment" if obj.shared_with_customer else "internal")
        elif isinstance(obj,NexotivaTicket):
            changed.setdefault(obj.request_id,set()).add("ticket")
    if not changed:return
    conn=db.connection()
    rows=conn.execute(select(Request.id,Request.requester_id,Request.assignee_id).where(Request.id.in_(changed))).all()
    scopes={"staff"}|{"user:"+str(uid) for row in rows for uid in row[1:] if uid is not None}|{"user:"+str(uid) for uid in old_owners}
    ins=pg_insert if conn.dialect.name=="postgresql" else sqlite_insert
    stmt=ins(SupportRevision).values([{"scope":scope,"revision":str(uuid4())} for scope in sorted(scopes)])
    conn.execute(stmt.on_conflict_do_update(index_elements=["scope"],set_={"revision":stmt.excluded.revision}))
    links=conn.execute(select(NexotivaTicket.request_id,NexotivaTicket.company_id,NexotivaTicket.user_id).where(NexotivaTicket.request_id.in_(changed))).all()
    for tid,cid,uid in links:
        for kind in sorted(changed[tid]-{"internal"}):
            conn.execute(SupportOutbox.__table__.insert().values(id=str(uuid4()),company_id=cid,user_id=uid,ticket_id=tid,kind=kind,created_at=datetime.now(timezone.utc)))

def scope_for(user):
    return "staff" if user.role in (UserRole.ADMIN,UserRole.ANALYST) else "user:"+str(user.id)
def revision(db,user):
    row=db.get(SupportRevision,scope_for(user),populate_existing=True)
    return row.revision if row else "0"
