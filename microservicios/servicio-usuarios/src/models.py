"""Modelos SQLAlchemy para el microservicio de Usuarios."""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class UsuarioEstado(str):
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    SUSPENDIDO = "suspendido"


class Usuario(Base):
    """Modelo de Usuario."""
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    direccion: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    estado: Mapped[str] = mapped_column(
        String(20), default=UsuarioEstado.ACTIVO, nullable=False
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relaciones
    historial: Mapped[List["HistorialUsuario"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, nombre={self.nombre}, email={self.email})>"


class HistorialUsuario(Base):
    """Modelo de historial de cambios de usuarios."""
    __tablename__ = "historial_usuarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )
    accion: Mapped[str] = mapped_column(String(50), nullable=False)
    datos_anteriores: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    datos_nuevos: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    fecha: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relaciones
    usuario: Mapped["Usuario"] = relationship(back_populates="historial")

    def __repr__(self) -> str:
        return f"<HistorialUsuario(id={self.id}, usuario_id={self.usuario_id}, accion={self.accion})>"
