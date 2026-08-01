"""Testes da validacao de seguranca para inicializacao em ambiente de producao."""
import pytest

from app.core.config import Settings


def test_producao_com_valores_padrao_falha():
    settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="troque-esta-chave-por-uma-chave-secreta-forte",
        ADMIN_PASSWORD="troque-esta-senha",
        DATABASE_URL="postgresql+psycopg2://postgres:postgres@db:5432/central_solicitacoes",
        CORS_ORIGINS="http://localhost:3000",
    )
    with pytest.raises(RuntimeError, match="Configuracao insegura"):
        settings.validate_for_production()


def test_producao_com_cors_aberto_falha():
    settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a" * 40,
        ADMIN_PASSWORD="SenhaForteComplexa123",
        DATABASE_URL="postgresql+psycopg2://appuser:senhaforte@db:5432/central_solicitacoes",
        CORS_ORIGINS="*",
    )
    with pytest.raises(RuntimeError, match="CORS_ORIGINS"):
        settings.validate_for_production()


def test_producao_com_valores_seguros_nao_falha():
    settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a" * 40,
        ADMIN_PASSWORD="SenhaForteComplexa123",
        DATABASE_URL="postgresql+psycopg2://appuser:senhaforte@db:5432/central_solicitacoes",
        CORS_ORIGINS="https://app.empresa.com",
    )
    settings.validate_for_production()  # nao deve levantar excecao


def test_desenvolvimento_com_valores_padrao_nao_falha():
    settings = Settings(ENVIRONMENT="development")
    settings.validate_for_production()  # sem efeito fora de producao
