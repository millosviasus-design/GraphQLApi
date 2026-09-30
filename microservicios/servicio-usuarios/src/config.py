"""Configuración del microservicio de Usuarios."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/usuarios_db"
    REDIS_URL: str = "redis://localhost:6379"
    PORT: int = 4001
    SERVICE_NAME: str = "servicio-usuarios"

    class Config:
        env_file = ".env"


settings = Settings()
