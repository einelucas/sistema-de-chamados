"""Configuracoes centrais da aplicacao, carregadas a partir de variaveis de ambiente."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Valores de exemplo usados no .env.example. Sao seguros apenas para desenvolvimento local;
# a aplicacao recusa iniciar em producao (ENVIRONMENT=production) caso qualquer um deles
# ainda esteja em uso, para evitar que credenciais de exemplo cheguem a um ambiente real.
_INSECURE_SECRET_KEYS = {"troque-esta-chave", "troque-esta-chave-por-uma-chave-secreta-forte"}
_INSECURE_ADMIN_PASSWORDS = {"troque-esta-senha"}
_INSECURE_DB_CREDENTIALS = {"postgres:postgres"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/central_solicitacoes"
    SECRET_KEY: str = "troque-esta-chave"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_NAME: str = "Administrador"
    ADMIN_PASSWORD: str = "troque-esta-senha"

    CORS_ORIGINS: str = "http://localhost:3000"

    UPLOAD_DIRECTORY: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    ALLOWED_UPLOAD_EXTENSIONS: str = ".pdf,.png,.jpg,.jpeg,.docx,.xlsx,.txt,.csv"

    ENVIRONMENT: str = "development"

    API_V1_PREFIX: str = "/api/v1"
    NEXOTIVA_INTEGRATION_TOKEN: str = ""
    NEXOTIVA_WEBHOOK_URL: str = ""
    NEXOTIVA_WEBHOOK_SECRET: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_upload_extensions_list(self) -> list[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_UPLOAD_EXTENSIONS.split(",") if ext.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    def validate_for_production(self) -> None:
        """Impede a inicializacao em producao com credenciais/configuracoes de exemplo.

        Chamado no startup da aplicacao (ver app/main.py). Nao tem efeito em desenvolvimento
        ou testes, apenas quando ENVIRONMENT=production.
        """
        if not self.is_production:
            return

        problems: list[str] = []

        if self.SECRET_KEY in _INSECURE_SECRET_KEYS or len(self.SECRET_KEY) < 32:
            problems.append(
                "SECRET_KEY insegura ou muito curta (minimo 32 caracteres). Gere uma chave "
                "forte, por exemplo com `openssl rand -hex 32`."
            )
        if self.ADMIN_PASSWORD in _INSECURE_ADMIN_PASSWORDS or len(self.ADMIN_PASSWORD) < 8:
            problems.append(
                "ADMIN_PASSWORD insegura ou muito curta (minimo 8 caracteres). Defina uma "
                "senha forte para o administrador inicial."
            )
        if any(cred in self.DATABASE_URL for cred in _INSECURE_DB_CREDENTIALS):
            problems.append(
                "DATABASE_URL utiliza a credencial padrao postgres:postgres. Configure um "
                "usuario e senha dedicados para o banco em producao."
            )
        if "*" in self.cors_origins_list:
            problems.append(
                "CORS_ORIGINS contem '*' (aberto para qualquer origem). Liste explicitamente "
                "os dominios autorizados do frontend em producao."
            )

        if problems:
            details = "\n  - ".join(problems)
            raise RuntimeError(
                "Configuracao insegura para ENVIRONMENT=production. Corrija antes de "
                f"iniciar a aplicacao:\n  - {details}"
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

