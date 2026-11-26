"""Agrega todos os roteadores da API v1."""
from fastapi import APIRouter

from app.api.routes import attachments, auth, comments, dashboard, history, requests, users

from app.api.routes import nexotiva, sync

api_router = APIRouter()
api_router.include_router(nexotiva.router)
api_router.include_router(sync.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(requests.router)
api_router.include_router(comments.router)
api_router.include_router(history.router)
api_router.include_router(attachments.router)
api_router.include_router(dashboard.router)
