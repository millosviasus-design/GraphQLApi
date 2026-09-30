"""Utilidades compartidas entre microservicios."""

import uuid
from datetime import datetime


def generate_uuid() -> str:
    """Genera un UUID único como string."""
    return str(uuid.uuid4())


def utcnow() -> datetime:
    """Retorna la fecha/hora actual en UTC."""
    return datetime.utcnow()
