# models/system.py
from typing import Optional
from sqlalchemy import String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class SystemSetting(Base):
    """Глобальные настройки системы."""
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)


class SystemLog(Base):
    """Журналирование важных событий (безопасность/аудит)."""
    __tablename__ = "system_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(100)) # e.g. "USER_LOGIN_FAILED"
    details: Mapped[Optional[str]] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String(20), default="INFO") # INFO, WARN, ERROR

    user = relationship("User")
