"""Modelos SQLAlchemy para el microservicio de Órdenes."""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class OrdenEstado:
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    ENVIADA = "enviada"
    ENTREGADA = "entregada"
    CANCELADA = "cancelada"


class Orden(Base):
    """Modelo de Orden."""
    __tablename__ = "ordenes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    estado: Mapped[str] = mapped_column(
        String(20), default=OrdenEstado.PENDIENTE, nullable=False
    )
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    moneda: Mapped[str] = mapped_column(String(3), default="MXN", nullable=False)
    direccion_envio: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relaciones
    items: Mapped[List["ItemOrden"]] = relationship(
        back_populates="orden", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Orden(id={self.id}, usuario_id={self.usuario_id}, total={self.total}, estado={self.estado})>"


class ItemOrden(Base):
    """Modelo de Item de Orden."""
    __tablename__ = "items_orden"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    orden_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ordenes.id"), nullable=False
    )
    producto_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    cantidad: Mapped[int] = mapped_column(Numeric(10), nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Relaciones
    orden: Mapped["Orden"] = relationship(back_populates="items")

    def __repr__(self) -> str:
        return f"<ItemOrden(id={self.id}, orden_id={self.orden_id}, producto_id={self.producto_id})>"
