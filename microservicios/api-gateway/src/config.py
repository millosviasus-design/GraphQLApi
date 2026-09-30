"""Configuración del API Gateway."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    USUARIOS_URL: str = "http://localhost:4001/graphql"
    PAGOS_URL: str = "http://localhost:4002/graphql"
    ORDENES_URL: str = "http://localhost:4003/graphql"
    PEDIDOS_URL: str = "http://localhost:4004/graphql"
    PORT: int = 4000

    class Config:
        env_file = ".env"


settings = Settings()
