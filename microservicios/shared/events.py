"""
Eventos compartidos entre microservicios.
Cada evento tiene un nombre único y un payload con la información relevante.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum
import json


class EventType(str, Enum):
    """Tipos de eventos del sistema."""
    # Usuarios
    USUARIO_CREADO = "usuario.creado"
    USUARIO_ACTUALIZADO = "usuario.actualizado"
    USUARIO_ELIMINADO = "usuario.eliminado"

    # Pagos
    PAGO_COMPLETADO = "pago.completado"
    PAGO_FALLIDO = "pago.fallido"
    PAGO_REEMBOLSADO = "pago.reembolsado"

    # Órdenes
    ORDEN_CREADA = "orden.creada"
    ORDEN_CONFIRMADA = "orden.confirmada"
    ORDEN_ENVIADA = "orden.enviada"
    ORDEN_ENTREGADA = "orden.entregada"
    ORDEN_CANCELADA = "orden.cancelada"

    # Pedidos
    PEDIDO_CREADO = "pedido.creado"
    PEDIDO_EN_CAMINO = "pedido.en_camino"
    PEDIDO_ENTREGADO = "pedido.entregado"
    PEDIDO_CANCELADO = "pedido.cancelado"


@dataclass
class Event:
    """Evento base del sistema."""
    type: EventType
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)


# Eventos de Usuarios
@dataclass
class UsuarioCreadoEvent(Event):
    def __init__(self, usuario_id: str, nombre: str, email: str, **kwargs):
        super().__init__(
            type=EventType.USUARIO_CREADO,
            payload={"usuario_id": usuario_id, "nombre": nombre, "email": email},
            **kwargs
        )


# Eventos de Pagos
@dataclass
class PagoCompletadoEvent(Event):
    def __init__(self, pago_id: str, orden_id: str, usuario_id: str, monto: float, **kwargs):
        super().__init__(
            type=EventType.PAGO_COMPLETADO,
            payload={
                "pago_id": pago_id,
                "orden_id": orden_id,
                "usuario_id": usuario_id,
                "monto": monto,
            },
            **kwargs
        )


@dataclass
class PagoFallidoEvent(Event):
    def __init__(self, pago_id: str, orden_id: str, motivo: str, **kwargs):
        super().__init__(
            type=EventType.PAGO_FALLIDO,
            payload={"pago_id": pago_id, "orden_id": orden_id, "motivo": motivo},
            **kwargs
        )


# Eventos de Órdenes
@dataclass
class OrdenCreadaEvent(Event):
    def __init__(self, orden_id: str, usuario_id: str, total: float, **kwargs):
        super().__init__(
            type=EventType.ORDEN_CREADA,
            payload={"orden_id": orden_id, "usuario_id": usuario_id, "total": total},
            **kwargs
        )


@dataclass
class OrdenConfirmadaEvent(Event):
    def __init__(self, orden_id: str, **kwargs):
        super().__init__(
            type=EventType.ORDEN_CONFIRMADA,
            payload={"orden_id": orden_id},
            **kwargs
        )


# Eventos de Pedidos
@dataclass
class PedidoCreadoEvent(Event):
    def __init__(self, pedido_id: str, orden_id: str, usuario_id: str, **kwargs):
        super().__init__(
            type=EventType.PEDIDO_CREADO,
            payload={"pedido_id": pedido_id, "orden_id": orden_id, "usuario_id": usuario_id},
            **kwargs
        )


@dataclass
class PedidoEntregadoEvent(Event):
    def __init__(self, pedido_id: str, orden_id: str, **kwargs):
        super().__init__(
            type=EventType.PEDIDO_ENTREGADO,
            payload={"pedido_id": pedido_id, "orden_id": orden_id},
            **kwargs
        )
