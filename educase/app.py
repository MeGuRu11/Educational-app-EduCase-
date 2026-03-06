# app.py
"""
Модульный синглтон приложения.
Хранит глобальное состояние: текущий пользователь, конфиг, контейнер.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from config import CONFIG, AppConfig
from core.database import Session

if TYPE_CHECKING:
    from core.di_container import Container

current_user = None  # type: ignore[assignment]  # User | None
config: AppConfig = CONFIG
container: Container | None = None


def get_session():
    """Всегда использовать через with: with get_session() as s: ..."""
    return Session()
