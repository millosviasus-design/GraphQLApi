"""Configuración del microservicio de Pedidos."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5435/pedidos_db"
    REDIS_URL: str = "redis://localhost:6379"
    PORT: int = 4004
    SERVICE_NAME: str = "servicio-pedidos"

    class Config:
        env_file = ".env"


settings = Settings()
