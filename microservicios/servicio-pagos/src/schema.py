"""Schema GraphQL para el microservicio de Pagos."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

import strawberry
from strawberry.federation import Schema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Pago, HistorialPago, PagoEstado, PagoMetodo


# ============== Types ==============

@strawberry.type
class PagoType:
    """Tipo GraphQL de Pago."""
    id: UUID
    orden_id: UUID
    usuario_id: UUID
    monto: Decimal
    moneda: str
    metodo: str
    estado: str
    referencia: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime


@strawberry.type
class HistorialPagoType:
    """Tipo GraphQL de Historial de Pago."""
    id: UUID
    pago_id: UUID
    estado_anterior: str
    estado_nuevo: str
    motivo: Optional[str] = None
    fecha: datetime


@strawberry.type
class PagoConnection:
    """Conexión de pagos para paginación."""
    items: List[PagoType]
    total: int


# ============== Inputs ==============

@strawberry.input
class ProcesarPagoInput:
    """Input para procesar un pago."""
    orden_id: UUID
    usuario_id: UUID
    monto: Decimal
    moneda: str = "MXN"
    metodo: str = PagoMetodo.TARJETA


@strawberry.input
class ReembolsarPagoInput:
    """Input para reembolsar un pago."""
    pago_id: UUID
    motivo: Optional[str] = None


# ============== Queries ==============

@strawberry.type
class Query:
    """Queries del microservicio de Pagos."""

    @strawberry.field
    async def obtener_pago(self, id: UUID, info: strawberry.types.Info) -> Optional[PagoType]:
        """Obtiene un pago por su ID."""
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(Pago).where(Pago.id == id))
        pago = result.scalar_one_or_none()
        return _map_pago(pago) if pago else None

    @strawberry.field
    async def listar_pagos(
        self,
        info: strawberry.types.Info,
        usuario_id: Optional[UUID] = None,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> PagoConnection:
        """Lista pagos con paginación y filtros."""
        db: AsyncSession = info.context["db"]
        query = select(Pago)
        if usuario_id:
            query = query.where(Pago.usuario_id == usuario_id)
        if estado:
            query = query.where(Pago.estado == estado)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        pagos = result.scalars().all()
        return PagoConnection(
            items=[_map_pago(p) for p in pagos],
            total=len(pagos),
        )

    @strawberry.field
    async def pagos_por_orden(
        self, orden_id: UUID, info: strawberry.types.Info
    ) -> List[PagoType]:
        """Obtiene todos los pagos de una orden."""
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(Pago).where(Pago.orden_id == orden_id))
        pagos = result.scalars().all()
        return [_map_pago(p) for p in pagos]


# ============== Mutations ==============

@strawberry.type
class Mutation:
    """Mutations del microservicio de Pagos."""

    @strawberry.mutation
    async def procesar_pago(
        self, input: ProcesarPagoInput, info: strawberry.types.Info
    ) -> PagoType:
        """Procesa un nuevo pago."""
        db: AsyncSession = info.context["db"]
        pago = Pago(
            orden_id=input.orden_id,
            usuario_id=input.usuario_id,
            monto=input.monto,
            moneda=input.moneda,
            metodo=input.metodo,
            estado=PagoEstado.COMPLETADO,
            referencia=f"REF-{uuid.uuid4().hex[:12].upper()}",
        )
        db.add(pago)
        await db.flush()
        await db.refresh(pago)

        # Registrar en historial
        historial = HistorialPago(
            pago_id=pago.id,
            estado_anterior="",
            estado_nuevo=PagoEstado.COMPLETADO,
            motivo="Pago procesado exitosamente",
        )
        db.add(historial)

        return _map_pago(pago)

    @strawberry.mutation
    async def reembolsar_pago(
        self, input: ReembolsarPagoInput, info: strawberry.types.Info
    ) -> Optional[PagoType]:
        """Reembolsa un pago."""
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(Pago).where(Pago.id == input.pago_id))
        pago = result.scalar_one_or_none()
        if not pago:
            return None

        estado_anterior = pago.estado
        pago.estado = PagoEstado.REEMBOLSADO

        # Registrar en historial
        historial = HistorialPago(
            pago_id=pago.id,
            estado_anterior=estado_anterior,
            estado_nuevo=PagoEstado.REEMBOLSADO,
            motivo=input.motivo,
        )
        db.add(historial)
        await db.flush()
        await db.refresh(pago)

        return _map_pago(pago)

    @strawberry.mutation
    async def marcar_pago_fallido(
        self, pago_id: UUID, motivo: str, info: strawberry.types.Info
    ) -> Optional[PagoType]:
        """Marca un pago como fallido."""
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(Pago).where(Pago.id == pago_id))
        pago = result.scalar_one_or_none()
        if not pago:
            return None

        estado_anterior = pago.estado
        pago.estado = PagoEstado.FALLIDO

        # Registrar en historial
        historial = HistorialPago(
            pago_id=pago.id,
            estado_anterior=estado_anterior,
            estado_nuevo=PagoEstado.FALLIDO,
            motivo=motivo,
        )
        db.add(historial)
        await db.flush()
        await db.refresh(pago)

        return _map_pago(pago)


# ============== Helpers ==============

def _map_pago(pago: Pago) -> PagoType:
    """Mapea un modelo Pago a PagoType."""
    return PagoType(
        id=pago.id,
        orden_id=pago.orden_id,
        usuario_id=pago.usuario_id,
        monto=pago.monto,
        moneda=pago.moneda,
        metodo=pago.metodo,
        estado=pago.estado,
        referencia=pago.referencia,
        fecha_creacion=pago.fecha_creacion,
        fecha_actualizacion=pago.fecha_actualizacion,
    )


# ============== Schema ==============

schema = Schema(query=Query, mutation=Mutation, enable_federation_2=True)
