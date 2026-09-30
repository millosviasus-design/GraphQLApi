"""Entry point del API Gateway."""

from contextlib import asynccontextmanager

import httpx
import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from src.config import settings


@strawberry.type
class Query:
    """Query passthrough - el gateway redirige a los microservicios."""

    @strawberry.field
    async def health(self) -> str:
        return "API Gateway OK"


@strawberry.type
class Mutation:
    """Mutation passthrough."""
    pass


schema = Schema(query=Query, mutation=Mutation)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación."""
    yield


app = FastAPI(title="API Gateway", lifespan=lifespan)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {"status": "ok", "service": "api-gateway"}


@app.get("/")
async def root():
    """Endpoint raíz."""
    return {
        "message": "API Gateway - Sistema de Microservicios",
        "services": {
            "usuarios": settings.USUARIOS_URL,
            "pagos": settings.PAGOS_URL,
            "ordenes": settings.ORDENES_URL,
            "pedidos": settings.PEDIDOS_URL,
        },
    }
