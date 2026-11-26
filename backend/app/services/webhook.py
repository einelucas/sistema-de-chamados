"""Bounded delivery with durable leases and retry on subsequent authorized requests."""
import hashlib,hmac,json,time
from datetime import datetime,timezone,timedelta
from urllib.parse import urlsplit
import httpx
from sqlalchemy import select,or_,delete
from app.models.support_sync import SupportOutbox
from app.core.config import settings
from app.database.session import SessionLocal

def configured():
    try:
        url=urlsplit(settings.NEXOTIVA_WEBHOOK_URL)
        return len(settings.NEXOTIVA_WEBHOOK_SECRET)>=32 and bool(url.hostname) and not(url.username or url.password or url.query or url.fragment) and (url.scheme=="https" or (not settings.is_production and url.scheme=="http" and url.hostname in ("localhost","127.0.0.1")))
    except ValueError:return False

def deliver_pending(limit=2):
    if not configured():return
    now=datetime.now(timezone.utc)
    with SessionLocal() as db:
        rows=db.scalars(select(SupportOutbox).where(SupportOutbox.delivered_at.is_(None),or_(SupportOutbox.lease_until.is_(None),SupportOutbox.lease_until<now)).order_by(SupportOutbox.created_at,SupportOutbox.id).limit(limit).with_for_update(skip_locked=True)).all()
        payloads=[]
        for row in rows:
            row.lease_until=now+timedelta(seconds=30)
            payloads.append({"id":row.id,"company_id":row.company_id,"user_id":row.user_id,"ticket_id":row.ticket_id,"kind":row.kind})
        db.commit()
    if not payloads:return
    with httpx.Client(timeout=1.5,follow_redirects=False) as client:
        for payload in payloads:
            data=json.dumps(payload,separators=(",",":"),sort_keys=True).encode()
            timestamp=str(int(time.time()))
            signature=hmac.new(settings.NEXOTIVA_WEBHOOK_SECRET.encode(),timestamp.encode()+b"."+data,hashlib.sha256).hexdigest()
            try:
                response=client.post(settings.NEXOTIVA_WEBHOOK_URL,content=data,headers={"Content-Type":"application/json","X-Nexotiva-Timestamp":timestamp,"X-Nexotiva-Signature":signature})
                if not 200<=response.status_code<300:continue
                with SessionLocal() as db:
                    row=db.get(SupportOutbox,payload["id"])
                    if row:row.delivered_at=datetime.now(timezone.utc)
                    db.commit()
            except httpx.RequestError:continue
    with SessionLocal() as db:
        db.execute(delete(SupportOutbox).where(SupportOutbox.delivered_at<now-timedelta(days=7)))
        db.commit()
