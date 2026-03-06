# core/db_maintenance.py
"""
Фоновое обслуживание БД: VACUUM, очистка старых логов, abandoned попыток.
Запускается через QTimer.singleShot(3000, ...) из main.py.
"""
from sqlalchemy import text

from config import DB_PATH
from core.database import engine


def run_maintenance() -> None:
    """VACUUM (если БД > 50MB) + очистка старых записей."""
    # VACUUM требует AUTOCOMMIT
    ac_engine = engine.execution_options(isolation_level="AUTOCOMMIT")
    with ac_engine.connect() as conn:
        if DB_PATH.exists() and DB_PATH.stat().st_size > 50 * 1024 * 1024:
            conn.execute(text("PRAGMA wal_checkpoint(FULL)"))
            conn.execute(text("VACUUM"))

    # Обычная очистка — в транзакции
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM system_logs WHERE timestamp < datetime('now', '-90 days')")
        )
        conn.execute(
            text(
                "UPDATE attempts SET status='abandoned' WHERE status='in_progress' "
                "AND started_at < datetime('now', '-30 days')"
            )
        )
