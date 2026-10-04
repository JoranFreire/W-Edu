from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/wedu"
    # Conexoes por processo da API: com N workers o banco recebe ate N * (POOL_SIZE + MAX_OVERFLOW).
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT_SECONDS: int = 10
    DB_POOL_RECYCLE_SECONDS: int = 1800
    # Dominio base para instituicao por subdominio (ex.: "wedu.com.br" -> escola.wedu.com.br). Vazio desativa.
    TENANT_BASE_DOMAIN: str | None = None
    TENANT_RESERVED_SUBDOMAINS: list[str] = ["www", "app", "api", "admin"]
    REDIS_URL: str = "redis://localhost:6379/2"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    # Login facial: chave publica Ed25519 (32 bytes, base64url) com que o Persona assina o
    # assertion de rosto conferido. Vazio desativa `POST /auth/facial-login`.
    PERSONA_ASSERTION_PUBLIC_KEY: str | None = None
    # Fuso dos horarios escritos nos avisos (ex.: passagem na catraca).
    DISPLAY_TIMEZONE: str = "America/Sao_Paulo"

    BEVOX_URL: str = "http://localhost:8001"
    BEVOX_PUBLIC_URL: str | None = None
    WMATRIX_URL: str = "http://localhost:8000"
    WOMNI_URL: str | None = None
    WOMNI_API_TOKEN: str | None = None
    NOTIFICATION_DISPATCH_TIMEOUT_SECONDS: float = 10.0
    NOTIFICATION_WORKER_ENABLED: bool = True
    NOTIFICATION_WORKER_INTERVAL_SECONDS: int = 60
    NOTIFICATION_WORKER_BATCH_SIZE: int = 100
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str | None = None
    SMTP_USE_TLS: bool = True
    ASAAS_API_URL: str = "https://api-sandbox.asaas.com/v3"
    ASAAS_API_TOKEN: str | None = None
    DOCUMENTS_STORAGE_DIR: str = str(Path(__file__).resolve().parents[2] / "storage" / "documents")
    CERTIFICATES_STORAGE_DIR: str = str(Path(__file__).resolve().parents[2] / "storage" / "certificates")
    ASSIGNMENTS_STORAGE_DIR: str = str(Path(__file__).resolve().parents[2] / "storage" / "assignments")
    VIDEOS_STORAGE_DIR: str = str(Path(__file__).resolve().parents[2] / "storage" / "videos")

    # Salario minimo de referencia (faixas de renda da prestacao de contas): tabela local sincronizada com a
    # serie 1619 do SGS do Banco Central a cada MINIMUM_WAGE_CACHE_HOURS. Vazio desliga a sincronizacao (vale a tabela).
    # O valor de reserva so e usado se a tabela nao tiver valor para a data.
    MINIMUM_WAGE_API_URL: str = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1619/dados"
    MINIMUM_WAGE_FALLBACK_CENTS: int = 162100
    MINIMUM_WAGE_CACHE_HOURS: int = 24

    ALLOWED_ORIGINS: list[str] = ["http://localhost:3002"]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
