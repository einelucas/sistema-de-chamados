"""One-time administrator provisioning from deployment configuration."""
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User
from app.models.enums import UserRole

def bootstrap_admin(db:Session):
    if not settings.BOOTSTRAP_ADMIN or not settings.is_production:return
    if len(settings.ADMIN_PASSWORD.encode("utf-8")) not in range(12,73):
        raise RuntimeError("Configure uma senha temporária de 12 a 72 bytes.")
    if db.scalar(select(User.id).limit(1)) is not None:return
    if db.bind.dialect.name=="postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(734019621)"))
    if db.scalar(select(User.id).limit(1)) is not None:return
    db.add(User(name=settings.ADMIN_NAME,email=settings.ADMIN_EMAIL.lower(),hashed_password=hash_password(settings.ADMIN_PASSWORD),role=UserRole.ADMIN,is_active=True,must_change_password=True))
    db.commit()
