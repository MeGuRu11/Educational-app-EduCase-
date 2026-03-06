# core/database.py
"""
SQLAlchemy engine, Session, PRAGMA-настройки для SQLite.
NullPool: каждый запрос — новое соединение (thread-safe).
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from config import DB_PATH

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    poolclass=NullPool,
    echo=False,
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, _):  # type: ignore[no-untyped-def]
    """Устанавливает PRAGMA при каждом новом соединении."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-32000")  # 32MB page cache
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.execute("PRAGMA busy_timeout=5000")  # Ждать 5с при блокировке
    cursor.close()


Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def run_migrations() -> None:
    """Обёртка над Alembic upgrade(head). Вызывается из main.py при старте."""
    from pathlib import Path

    from alembic import command
    from alembic.config import Config

    BASE_DIR = Path(__file__).parent.parent
    cfg = Config(str(BASE_DIR / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{DB_PATH}")
    command.upgrade(cfg, "head")
