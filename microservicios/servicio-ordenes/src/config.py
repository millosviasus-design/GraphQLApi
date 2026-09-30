"""Configuración del microservicio de Órdenes."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5434/ordenes_db"
    REDIS_URL: str = "redis://localhost:6379"
    PORT: int = 4003
    SERVICE_NAME: str = "servicio-ordenes"

    class Config:
        env_file = ".env"


settings = Settings()
