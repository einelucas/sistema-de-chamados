"""Configuracao da engine e das sessoes do SQLAlchemy."""
from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

options={"pool_pre_ping":True,"future":True,"hide_parameters":True}
if make_url(settings.DATABASE_URL).get_backend_name()=="postgresql":
    options.update(pool_size=3,max_overflow=2,pool_timeout=10,pool_recycle=300,connect_args={"connect_timeout":10})
engine = create_engine(settings.DATABASE_URL, **options)
if engine.dialect.name=="postgresql":
    @event.listens_for(engine,"begin")
    def transaction_timeout(conn):
        conn.exec_driver_sql("SET LOCAL statement_timeout='30s'")

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
