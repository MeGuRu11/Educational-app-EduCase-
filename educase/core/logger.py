# core/logger.py
"""
Структурированное логирование через loguru.
Ротация 7 дней, отдельный файл для ошибок.
Sink в system_logs таблицу БД (при наличии engine).
"""
from __future__ import annotations

import sys

from loguru import logger

from config import LOG_DIR


def setup_logger() -> None:
    """Настройка логирования. Вызывается в main.py после _init_dirs()."""
    # Убираем дефолтный обработчик stderr
    logger.remove()

    # Консоль (только при разработке)
    logger.add(
        sys.stderr,
        level="DEBUG",
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # Файл: ежедневная ротация, хранить 7 дней
    logger.add(
        LOG_DIR / "app_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="7 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8",
    )

    # Только ошибки — отдельный файл
    logger.add(
        LOG_DIR / "errors.log",
        rotation="10 MB",
        retention="30 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8",
    )


def log_to_db(user_id: int | None, level: str, action: str, details: str = "") -> None:
    """Запись в system_logs таблицу. Вызывается из сервисов для аудита."""
    try:
        from core.database import engine
        from sqlalchemy import text

        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO system_logs(user_id, level, action, details) "
                    "VALUES(:uid, :lvl, :act, :det)"
                ),
                {"uid": user_id, "lvl": level, "act": action, "det": details},
            )
    except Exception:
        # Если БД недоступна — логируем только в файл
        logger.warning(f"DB log failed: {action}")
