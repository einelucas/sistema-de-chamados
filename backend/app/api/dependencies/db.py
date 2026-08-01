"""Dependencia de sessao de banco de dados para os endpoints."""
from app.database.session import get_db

__all__ = ["get_db"]
