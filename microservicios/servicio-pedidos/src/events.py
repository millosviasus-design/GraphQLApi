"""Publicador de eventos para el microservicio de Pedidos."""

import json
import redis.asyncio as redis
from src.config import settings


class EventPublisher:
    """Publicador de eventos a Redis."""

    def __init__(self):
        self._redis: redis.Redis | None = None

    async def connect(self):
        """Conecta a Redis."""
        self._redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def disconnect(self):
        """Desconecta de Redis."""
        if self._redis:
            await self._redis.close()

    async def publish(self, event_type: str, payload: dict):
        """Publica un evento en Redis."""
        if not self._redis:
            await self.connect()
        event = {
            "type": event_type,
            "payload": payload,
            "source": settings.SERVICE_NAME,
        }
        await self._redis.publish(f"events:{event_type}", json.dumps(event))


publisher = EventPublisher()
