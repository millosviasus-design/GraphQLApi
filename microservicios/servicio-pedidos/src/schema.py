"""Schema GraphQL para el microservicio de Pedidos."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime

import strawberry
from strawberry.federation import Schema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Pedido, HistorialPedido, PedidoEstado


# ============== Types ==============

@strawberry.type
class DireccionEntrega:
    """Tipo de dirección de entrega."""
    calle: str
    ciudad: str
    estado: Optional[str] = None
    codigo_postal: Optional[str] = None
    pais: str = "México"


@strawberry.type
class PedidoType:
    """Tipo GraphQL de Pedido."""
    id: UUID
    orden_id: UUID
    usuario_id: UUID
    estado: str
    direccion_entrega: Optional[DireccionEntrega] = None
    fecha_entrega_estimada: Optional[datetime] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime


@strawberry.type
class HistorialPedidoType:
    """Tipo GraphQL de Historial de Pedido."""
    id: UUID
    pedido_id: UUID
    estado_anterior: str
    estado_nuevo: str
    comentario: Optional[str] = None
    fecha: datetime


@strawberry.type
class PedidoConnection:
    """Conexión de pedidos para paginación."""
    items: List[PedidoType]
    total: int


# ============== Inputs ==============

@strawberry.input
class CrearPedidoInput:
    """Input para crear un pedido."""
    orden_id: UUID
    usuario_id: UUID
    direccion_entrega: Optional[DireccionEntrega] = None
    fecha_entrega_estimada: Optional[datetime] = None


@strawberry.input
class ActualizarEstadoPedidoInput:
    """Input para actualizar estado de pedido."""
    pedido_id: UUID
    estado: str
    comentario: Optional[str] = None


# ============== Queries ==============

@strawberry.type
class Query:
    """Queries del microservicio de Pedidos."""

    @strawberry.field
    async def obtener_pedido(self, id: UUID, info: strawberry.types.Info) -> Optional[PedidoType]:
        """Obtiene un pedido por su ID."""
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(Pedido).where(Pedido.id == id))
        pedido = result.scalar_one_or_none()
        return _map_pedido(pedido) if pedido else None

    @strawberry.field
    async def listar_pedidos(
        self,
        info: strawberry.types.Info,
        usuario_id: Optional[UUID] = None,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> PedidoConnection:
        """Lista pedidos con paginación y filtros."""
        db: AsyncSession = info.context["db"]
        query = select(Pedido)
        if usuario_id:
            query = query.where(Pedido.usuario_id == usuario_id)
        if estado:
            query = query.where(Pedido.estado == estado)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        pedidos = result.scalars().all()
        return PedidoConnection(
            items=[_map_pedido(p) for p in pedidos],
            total=len(pedidos),
        )

    @strawberry.field
    async def pedidos_por_orden(
        self, orden_id: UUID, info: strawberry.types.Info
    ) -> List[PedidoType]:
        """Obtiene todos los pedidos de una orden."""
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(Pedido).where(Pedido.orden_id == orden_id))
        pedidos = result.scalars().all()
        return [_map_pedido(p) for p in pedidos]


# ============== Mutations ==============

@strawberry.type
class Mutation:
    """Mutations del microservicio de Pedidos."""

    @strawberry.mutation
    async def crear_pedido(
        self, input: CrearPedidoInput, info: strawberry.types.Info
    ) -> PedidoType:
        """Crea un nuevo pedido."""
        db: AsyncSession = info.context["db"]
        pedido = Pedido(
            orden_id=input.orden_id,
            usuario_id=input.usuario_id,
            direccion_entrega=input.direccion_entrega.__dict__ if input.direccion_entrega else None,
            fecha_entrega_estimada=input.fecha_entrega_estimada,
            estado=PedidoEstado.PREPARACION,
        )
        db.add(pedido)
        await db.flush()
        await db.refresh(pedido)

        # Registrar en historial
        historial = HistorialPedido(
            pedido_id=pedido.id,
            estado_anterior="",
            estado_nuevo=PedidoEstado.PREPARACION,
            comentario="Pedido creado",
        )
        db.add(historial)

        return _map_pedido(pedido)

    @strawberry.mutation
    async def actualizar_estado_pedido(
        self, input: ActualizarEstadoPedidoInput, info: strawberry.types.Info
    ) -> Optional[PedidoType]:
        """Actualiza el estado de un pedido."""
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(Pedido).where(Pedido.id == input.pedido_id))
        pedido = result.scalar_one_or_none()
        if not pedido:
            return None

        estado_anterior = pedido.estado
        pedido.estado = input.estado

        # Registrar en historial
        historial = HistorialPedido(
            pedido_id=pedido.id,
            estado_anterior=estado_anterior,
            estado_nuevo=input.estado,
            comentario=input.comentario,
        )
        db.add(historial)
        await db.flush()
        await db.refresh(pedido)

        return _map_pedido(pedido)


# ============== Helpers ==============

def _map_pedido(pedido: Pedido) -> PedidoType:
    """Mapea un modelo Pedido a PedidoType."""
    direccion = None
    if pedido.direccion_entrega:
        direccion = DireccionEntrega(**pedido.direccion_entrega)
    return PedidoType(
        id=pedido.id,
        orden_id=pedido.orden_id,
        usuario_id=pedido.usuario_id,
        estado=pedido.estado,
        direccion_entrega=direccion,
        fecha_entrega_estimada=pedido.fecha_entrega_estimada,
        fecha_creacion=pedido.fecha_creacion,
        fecha_actualizacion=pedido.fecha_actualizacion,
    )


# ============== Schema ==============

schema = Schema(query=Query, mutation=Mutation, enable_federation_2=True)
