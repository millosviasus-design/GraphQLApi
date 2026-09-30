"""Configuración del microservicio de Pagos."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/pagos_db"
    REDIS_URL: str = "redis://localhost:6379"
    PORT: int = 4002
    SERVICE_NAME: str = "servicio-pagos"

    class Config:
        env_file = ".env"


settings = Settings()
