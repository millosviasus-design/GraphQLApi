"""Schema GraphQL para el microservicio de Usuarios."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime

import strawberry
from strawberry.federation import Schema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Usuario, HistorialUsuario, UsuarioEstado


# ============== Types ==============

@strawberry.type
class Direccion:
    """Tipo de dirección."""
    calle: str
    ciudad: str
    estado: Optional[str] = None
    codigo_postal: Optional[str] = None
    pais: str = "México"


@strawberry.type
class UsuarioType:
    """Tipo GraphQL de Usuario."""
    id: UUID
    nombre: str
    email: str
    telefono: Optional[str] = None
    direccion: Optional[Direccion] = None
    estado: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime


@strawberry.type
class HistorialUsuarioType:
    """Tipo GraphQL de Historial de Usuario."""
    id: UUID
    usuario_id: UUID
    accion: str
    fecha: datetime


@strawberry.type
class UsuarioConnection:
    """Conexión de usuarios para paginación."""
    items: List[UsuarioType]
    total: int


# ============== Inputs ==============

@strawberry.input
class CrearUsuarioInput:
    """Input para crear un usuario."""
    nombre: str
    email: str
    telefono: Optional[str] = None
    direccion: Optional[Direccion] = None


@strawberry.input
class ActualizarUsuarioInput:
    """Input para actualizar un usuario."""
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[Direccion] = None
    estado: Optional[str] = None


# ============== Queries ==============

@strawberry.type
class Query:
    """Queries del microservicio de Usuarios."""

    @strawberry.field
    async def obtener_usuario(self, id: UUID, info: strawberry.types.Info) -> Optional[UsuarioType]:
        """Obtiene un usuario por su ID."""
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(Usuario).where(Usuario.id == id))
        usuario = result.scalar_one_or_none()
        return _map_usuario(usuario) if usuario else None

    @strawberry.field
    async def listar_usuarios(
        self,
        info: strawberry.types.Info,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> UsuarioConnection:
        """Lista usuarios con paginación y filtros."""
        db: AsyncSession = info.context["db"]
        query = select(Usuario)
        if estado:
            query = query.where(Usuario.estado == estado)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        usuarios = result.scalars().all()
        return UsuarioConnection(
            items=[_map_usuario(u) for u in usuarios],
            total=len(usuarios),
        )

    @strawberry.field
    async def buscar_usuarios(
        self,
        info: strawberry.types.Info,
        query: str,
        skip: int = 0,
        limit: int = 10,
    ) -> UsuarioConnection:
        """Busca usuarios por nombre o email."""
        db: AsyncSession = info.context["db"]
        search = f"%{query}%"
        stmt = select(Usuario).where(
            (Usuario.nombre.ilike(search)) | (Usuario.email.ilike(search))
        ).offset(skip).limit(limit)
        result = await db.execute(stmt)
        usuarios = result.scalars().all()
        return UsuarioConnection(
            items=[_map_usuario(u) for u in usuarios],
            total=len(usuarios),
        )


# ============== Mutations ==============

@strawberry.type
class Mutation:
    """Mutations del microservicio de Usuarios."""

    @strawberry.mutation
    async def crear_usuario(
        self, input: CrearUsuarioInput, info: strawberry.types.Info
    ) -> UsuarioType:
        """Crea un nuevo usuario."""
        db: AsyncSession = info.context["db"]
        usuario = Usuario(
            nombre=input.nombre,
            email=input.email,
            telefono=input.telefono,
            direccion=inputdireccion.__dict__ if input.direccion else None,
            estado=UsuarioEstado.ACTIVO,
        )
        db.add(usuario)
        await db.flush()
        await db.refresh(usuario)

        # Registrar en historial
        historial = HistorialUsuario(
            usuario_id=usuario.id,
            accion="creacion",
            datos_nuevos={
                "nombre": usuario.nombre,
                "email": usuario.email,
                "telefono": usuario.telefono,
            },
        )
        db.add(historial)

        return _map_usuario(usuario)

    @strawberry.mutation
    async def actualizar_usuario(
        self, id: UUID, input: ActualizarUsuarioInput, info: strawberry.types.Info
    ) -> Optional[UsuarioType]:
        """Actualiza un usuario existente."""
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(Usuario).where(Usuario.id == id))
        usuario = result.scalar_one_or_none()
        if not usuario:
            return None

        datos_anteriores = {
            "nombre": usuario.nombre,
            "email": usuario.email,
            "telefono": usuario.telefono,
            "estado": usuario.estado,
        }

        if input.nombre is not None:
            usuario.nombre = input.nombre
        if input.email is not None:
            usuario.email = input.email
        if input.telefono is not None:
            usuario.telefono = input.telefono
        if input.direccion is not None:
            usuario.direccion = input.direccion.__dict__
        if input.estado is not None:
            usuario.estado = input.estado

        # Registrar en historial
        historial = HistorialUsuario(
            usuario_id=usuario.id,
            accion="actualizacion",
            datos_anteriores=datos_anteriores,
            datos_nuevos={
                "nombre": usuario.nombre,
                "email": usuario.email,
                "telefono": usuario.telefono,
                "estado": usuario.estado,
            },
        )
        db.add(historial)
        await db.flush()
        await db.refresh(usuario)

        return _map_usuario(usuario)

    @strawberry.mutation
    async def eliminar_usuario(self, id: UUID, info: strawberry.types.Info) -> bool:
        """Elimina un usuario (soft delete - cambia estado a inactivo)."""
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(Usuario).where(Usuario.id == id))
        usuario = result.scalar_one_or_none()
        if not usuario:
            return False

        usuario.estado = UsuarioEstado.INACTIVO

        # Registrar en historial
        historial = HistorialUsuario(
            usuario_id=usuario.id,
            accion="eliminacion",
            datos_anteriores={"estado": UsuarioEstado.ACTIVO},
            datos_nuevos={"estado": UsuarioEstado.INACTIVO},
        )
        db.add(historial)
        await db.flush()

        return True


# ============== Helpers ==============

def _map_usuario(usuario: Usuario) -> UsuarioType:
    """Mapea un modelo Usuario a UsuarioType."""
    direccion = None
    if usuario.direccion:
        direccion = Direccion(**usuario.direccion)
    return UsuarioType(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        telefono=usuario.telefono,
        direccion=direccion,
        estado=usuario.estado,
        fecha_creacion=usuario.fecha_creacion,
        fecha_actualizacion=usuario.fecha_actualizacion,
    )


# ============== Schema ==============

schema = Schema(query=Query, mutation=Mutation, enable_federation_2=True)
