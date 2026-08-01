"""Ponto de entrada da aplicacao FastAPI."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
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
