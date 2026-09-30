"""Modelos SQLAlchemy para el microservicio de Pagos."""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, ForeignKey, Text, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class PagoEstado:
    PENDIENTE = "pendiente"
    COMPLETADO = "completado"
    FALLIDO = "fallido"
    REEMBOLSADO = "reembolsado"


class PagoMetodo:
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    PAYPAL = "paypal"


class Pago(Base):
    """Modelo de Pago."""
    __tablename__ = "pagos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    orden_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    usuario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    monto: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    moneda: Mapped[str] = mapped_column(String(3), default="MXN", nullable=False)
    metodo: Mapped[str] = mapped_column(String(20), nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20), default=PagoEstado.PENDIENTE, nullable=False
    )
    referencia: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relaciones
    historial: Mapped[List["HistorialPago"]] = relationship(
        back_populates="pago", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Pago(id={self.id}, orden_id={self.orden_id}, monto={self.monto}, estado={self.estado})>"


class HistorialPago(Base):
    """Modelo de historial de pagos."""
    __tablename__ = "historial_pagos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pago_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pagos.id"), nullable=False
    )
    estado_anterior: Mapped[str] = mapped_column(String(20), nullable=False)
    estado_nuevo: Mapped[str] = mapped_column(String(20), nullable=False)
    motivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relaciones
    pago: Mapped["Pago"] = relationship(back_populates="historial")

    def __repr__(self) -> str:
        return f"<HistorialPago(id={self.id}, pago_id={self.pago_id}, estado={self.estado_nuevo})>"
