# config.py
"""
Конфигурация приложения EduCase.
AppConfig, DATA_DIR, MEDIA_LIMITS, пути ко всем директориям данных.
"""
import json
import os
from dataclasses import dataclass, asdict, fields
from pathlib import Path
from typing import Literal

APP_NAME = "EduCase"
APP_VERSION = "1.0.0"
APP_AUTHOR = "ВМедА им. С.М. Кирова"

if os.name == "nt":
    DATA_DIR = Path(os.environ["APPDATA"]) / APP_NAME
else:
    DATA_DIR = Path.home() / f".{APP_NAME.lower()}"

DB_PATH = DATA_DIR / "educase.db"
LOG_DIR = DATA_DIR / "logs"
MEDIA_DIR = DATA_DIR / "media"
BACKUP_DIR = DATA_DIR / "backups"
CONFIG_PATH = DATA_DIR / "config.json"


def _init_dirs() -> None:
    """Создаёт все необходимые директории. Вызывается в main.py ДО build_container()."""
    for d in [
        DATA_DIR,
        LOG_DIR,
        MEDIA_DIR,
        BACKUP_DIR,
        MEDIA_DIR / "covers",
        MEDIA_DIR / "task_images",
        MEDIA_DIR / "avatars",
        MEDIA_DIR / "exports",
    ]:
        d.mkdir(parents=True, exist_ok=True)


MEDIA_LIMITS = {
    "cover": {"max_bytes": 2 * 1024 * 1024, "formats": ["png", "jpg", "jpeg"]},
    "task_image": {"max_bytes": 5 * 1024 * 1024, "formats": ["png", "jpg", "jpeg", "gif"]},
    "avatar": {"max_bytes": 512 * 1024, "formats": ["png", "jpg", "jpeg"]},
}

MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 300


@dataclass
class AppConfig:
    theme: Literal["light", "dark"] = "light"
    accent_color: str = "#0078D4"
    font_size_base: int = 13
    sidebar_expanded: bool = True
    auto_backup: bool = True
    backup_count: int = 7
    language: str = "ru"
    window_width: int = 1280
    window_height: int = 800
    window_maximized: bool = False
    animations_enabled: bool = True
    animation_speed: float = 1.0  # 0.5=быстрее, 2.0=медленнее

    @classmethod
    def load(cls) -> "AppConfig":
        try:
            raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            # Фильтруем лишние ключи — защита от несовместимости версий
            valid = {f.name for f in fields(cls)}
            return cls(**{k: v for k, v in raw.items() if k in valid})
        except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
            return cls()  # fallback на дефолты

    def save(self) -> None:
        CONFIG_PATH.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


CONFIG = AppConfig.load()
