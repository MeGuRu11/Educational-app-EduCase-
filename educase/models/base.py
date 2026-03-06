# models/base.py
"""
Базовый класс для всех моделей SQLAlchemy и общие Mixin'ы.
"""
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class TimestampMixin:
    """Миксин для добавления полей created_at и updated_at."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

__all__ = ["Base", "TimestampMixin"]
