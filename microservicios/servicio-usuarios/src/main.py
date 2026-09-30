"""Entry point del microservicio de Usuarios."""

from contextlib import asynccontextmanager

import strawberry
from fastapi import FastAPI, Depends
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import init_db, get_db
from src.schema import schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación."""
    await init_db()
    yield


app = FastAPI(title="Microservicio de Usuarios", lifespan=lifespan)


async def get_context(db: AsyncSession = Depends(get_db)):
    """Contexto para GraphQL."""
    return {"db": db}


graphql_app = GraphQLRouter(schema, context_getter=get_context)

app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {"status": "ok", "service": "usuarios"}
