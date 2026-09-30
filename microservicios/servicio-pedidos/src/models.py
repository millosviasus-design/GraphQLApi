"""Modelos SQLAlchemy para el microservicio de Pedidos."""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class PedidoEstado:
    PREPARACION = "preparacion"
    EN_CAMINO = "en_camino"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"


class Pedido(Base):
    """Modelo de Pedido."""
    __tablename__ = "pedidos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    orden_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    usuario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    estado: Mapped[str] = mapped_column(
        String(20), default=PedidoEstado.PREPARACION, nullable=False
    )
    direccion_entrega: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    fecha_entrega_estimada: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relaciones
    historial: Mapped[List["HistorialPedido"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Pedido(id={self.id}, orden_id={self.orden_id}, estado={self.estado})>"


class HistorialPedido(Base):
    """Modelo de historial de pedidos."""
    __tablename__ = "historial_pedidos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pedido_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pedidos.id"), nullable=False
    )
    estado_anterior: Mapped[str] = mapped_column(String(20), nullable=False)
    estado_nuevo: Mapped[str] = mapped_column(String(20), nullable=False)
    comentario: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relaciones
    pedido: Mapped["Pedido"] = relationship(back_populates="historial")

    def __repr__(self) -> str:
        return f"<HistorialPedido(id={self.id}, pedido_id={self.pedido_id}, estado={self.estado_nuevo})>"
