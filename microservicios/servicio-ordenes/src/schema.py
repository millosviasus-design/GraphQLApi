"""Schema GraphQL para el microservicio de Órdenes."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

import strawberry
from strawberry.federation import Schema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Orden, ItemOrden, OrdenEstado


# ============== Types ==============

@strawberry.type
class DireccionEnvio:
    """Tipo de dirección de envío."""
    calle: str
    ciudad: str
    estado: Optional[str] = None
    codigo_postal: Optional[str] = None
    pais: str = "México"


@strawberry.type
class ItemOrdenType:
    """Tipo GraphQL de Item de Orden."""
    id: UUID
    orden_id: UUID
    producto_id: UUID
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


@strawberry.type
class OrdenType:
    """Tipo GraphQL de Orden."""
    id: UUID
    usuario_id: UUID
    estado: str
    total: Decimal
    moneda: str
    direccion_envio: Optional[DireccionEnvio] = None
    items: List[ItemOrdenType]
    fecha_creacion: datetime
    fecha_actualizacion: datetime


@strawberry.type
class OrdenConnection:
    """Conexión de órdenes para paginación."""
    items: List[OrdenType]
    total: int


# ============== Inputs ==============

@strawberry.input
class ItemOrdenInput:
    """Input para item de orden."""
    producto_id: UUID
    cantidad: int
    precio_unitario: Decimal


@strawberry.input
class CrearOrdenInput:
    """Input para crear una orden."""
    usuario_id: UUID
    items: List[ItemOrdenInput]
    moneda: str = "MXN"
    direccion_envio: Optional[DireccionEnvio] = None


@strawberry.input
class ActualizarEstadoOrdenInput:
    """Input para actualizar estado de orden."""
    orden_id: UUID
    estado: str


# ============== Queries ==============

@strawberry.type
class Query:
    """Queries del microservicio de Órdenes."""

    @strawberry.field
    async def obtener_orden(self, id: UUID, info: strawberry.types.Info) -> Optional[OrdenType]:
        """Obtiene una orden por su ID."""
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(Orden).where(Orden.id == id))
        orden = result.scalar_one_or_none()
        if not orden:
            return None
        # Cargar items
        items_result = await db.execute(select(ItemOrden).where(ItemOrden.orden_id == orden.id))
        items = items_result.scalars().all()
        return _map_orden(orden, items)

    @strawberry.field
    async def listar_ordenes(
        self,
        info: strawberry.types.Info,
        usuario_id: Optional[UUID] = None,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> OrdenConnection:
        """Lista órdenes con paginación y filtros."""
        db: AsyncSession = info.context["db"]
        query = select(Orden)
        if usuario_id:
            query = query.where(Orden.usuario_id == usuario_id)
        if estado:
            query = query.where(Orden.estado == estado)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        ordenes = result.scalars().all()
        items_map = {}
        for orden in ordenes:
            items_result = await db.execute(select(ItemOrden).where(ItemOrden.orden_id == orden.id))
            items_map[orden.id] = items_result.scalars().all()
        return OrdenConnection(
            items=[_map_orden(o, items_map.get(o.id, [])) for o in ordenes],
            total=len(ordenes),
        )


# ============== Mutations ==============

@strawberry.type
class Mutation:
    """Mutations del microservicio de Órdenes."""

    @strawberry.mutation
    async def crear_orden(
        self, input: CrearOrdenInput, info: strawberry.types.Info
    ) -> OrdenType:
        """Crea una nueva orden."""
        db: AsyncSession = info.context["db"]
        total = sum(item.cantidad * item.precio_unitario for item in input.items)
        orden = Orden(
            usuario_id=input.usuario_id,
            total=total,
            moneda=input.moneda,
            direccion_envio=input.direccion_envio.__dict__ if input.direccion_envio else None,
            estado=OrdenEstado.PENDIENTE,
        )
        db.add(orden)
        await db.flush()

        # Crear items
        for item_input in input.items:
            item = ItemOrden(
                orden_id=orden.id,
                producto_id=item_input.producto_id,
                cantidad=item_input.cantidad,
                precio_unitario=item_input.precio_unitario,
                subtotal=item_input.cantidad * item_input.precio_unitario,
            )
            db.add(item)

        await db.flush()
        await db.refresh(orden)

        # Cargar items para respuesta
        items_result = await db.execute(select(ItemOrden).where(ItemOrden.orden_id == orden.id))
        items = items_result.scalars().all()

        return _map_orden(orden, items)

    @strawberry.mutation
    async def actualizar_estado_orden(
        self, input: ActualizarEstadoOrdenInput, info: strawberry.types.Info
    ) -> Optional[OrdenType]:
        """Actualiza el estado de una orden."""
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(Orden).where(Orden.id == input.orden_id))
        orden = result.scalar_one_or_none()
        if not orden:
            return None

        orden.estado = input.estado
        await db.flush()
        await db.refresh(orden)

        # Cargar items
        items_result = await db.execute(select(ItemOrden).where(ItemOrden.orden_id == orden.id))
        items = items_result.scalars().all()

        return _map_orden(orden, items)


# ============== Helpers ==============

def _map_orden(orden: Orden, items: List[ItemOrden]) -> OrdenType:
    """Mapea un modelo Orden a OrdenType."""
    direccion = None
    if orden.direccion_envio:
        direccion = DireccionEnvio(**orden.direccion_envio)
    return OrdenType(
        id=orden.id,
        usuario_id=orden.usuario_id,
        estado=orden.estado,
        total=orden.total,
        moneda=orden.moneda,
        direccion_envio=direccion,
        items=[
            ItemOrdenType(
                id=item.id,
                orden_id=item.orden_id,
                producto_id=item.producto_id,
                cantidad=int(item.cantidad),
                precio_unitario=item.precio_unitario,
                subtotal=item.subtotal,
            )
            for item in items
        ],
        fecha_creacion=orden.fecha_creacion,
        fecha_actualizacion=orden.fecha_actualizacion,
    )


# ============== Schema ==============

schema = Schema(query=Query, mutation=Mutation, enable_federation_2=True)
