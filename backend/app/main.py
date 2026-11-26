"""Ponto de entrada da aplicacao FastAPI."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.concurrency import run_in_threadpool
from app.services import webhook
from uuid import uuid4
from time import perf_counter
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.core.exceptions import AppError, app_error_handler, unhandled_exception_handler
from app.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

# Falha rapido: se ENVIRONMENT=production e alguma configuracao insegura de exemplo ainda
# estiver em uso (SECRET_KEY, senha do admin, credenciais padrao do banco, CORS aberto),
# a aplicacao nao deve nem iniciar o servidor.
settings.validate_for_production()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Central de Solicitacoes API iniciada em modo %s", settings.ENVIRONMENT)
    yield
    logger.info("Central de Solicitacoes API finalizada")


app = FastAPI(
    title="Central de Solicitacoes - API",
    description="API para gerenciamento de solicitacoes internas (chamados).",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

@app.middleware("http")
async def request_metadata(request:Request,call_next):
    start=perf_counter()
    response=await call_next(request)
    response.headers["X-Request-ID"]=str(uuid4())
    if not response.headers.get("content-type","").startswith("text/event-stream"):
        response.headers["Cache-Control"]="no-store"
    if webhook.configured() and response.status_code<300 and (request.method in ("POST","PUT","PATCH","DELETE") or request.url.path.endswith("/sync/version")):
        try:await run_in_threadpool(webhook.deliver_pending)
        except Exception:logger.warning("Entrega de webhook adiada; outbox preservada")
    logger.info("route=%s method=%s status=%d ms=%.1f",getattr(request.scope.get("route"),"path","unknown"),request.method,response.status_code,(perf_counter()-start)*1000)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Status"], summary="Verifica se a API esta no ar")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "central-solicitacoes-api"}


@app.get("/health", tags=["Status"], summary="Health check para orquestradores")
def health() -> dict[str, str]:
    return {"status": "healthy"}
