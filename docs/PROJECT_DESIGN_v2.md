# EduCase — Интерактивная Образовательная Платформа

## Полная Проектная Документация v2.0 — ПОЛНЫЙ АУДИТ

> Версия 2.0 | Дата: 2026-03-04 | Статус: Расширенная и проверенная

---

## CHANGELOG v1.0 → v2.0 (что добавлено)

| Раздел             | Что добавлено                                                             |
| ------------------ | ------------------------------------------------------------------------- |
| Зависимости        | Полный `requirements.txt` с точными версиями + обоснование каждой         |
| БД                 | Полная схема: все индексы, constraints, триггеры, WAL-режим, вакуум       |
| Архитектура        | DI-контейнер, EventBus, threading-модель, стратегия ошибок                |
| UI                 | Детальное описание **каждого** экрана (21 экран) — все виджеты, состояния |
| Анимации           | Полная спецификация каждой анимации с параметрами Qt                      |
| SVG-иконки         | Полный каталог 55 иконок inline в Python                                  |
| Компоненты         | Все переиспользуемые виджеты с полным API                                 |
| Config             | Полная система конфигурации (файл + env + runtime)                        |
| Безопасность       | Стратегия хэширования, сессия, защита от инъекций                         |
| Файловое хранилище | Стратегия хранения медиафайлов, именование, лимиты                        |
| TODO               | Детализированы все шаги, добавлены пропущенные задачи                     |

---

## 1. ПОЛНЫЙ СТЕК ЗАВИСИМОСТЕЙ

### 1.1 requirements.txt (production)

```
# ── CORE GUI ────────────────────────────────────────────────────────────────
PySide6==6.7.3                  # Qt6 GUI-фреймворк (LGPL)
# ✅ PySide6-Addons и PySide6-Essentials — авто-зависимости PySide6, не нужно указывать отдельно

# ── DATABASE ────────────────────────────────────────────────────────────────
SQLAlchemy==2.0.36              # ORM (async-ready, 2.x API)
alembic==1.14.0                 # Миграции схемы БД

# ── SECURITY ────────────────────────────────────────────────────────────────
bcrypt==4.2.1                   # Хэширование паролей (cost=12)
# ✅ cryptography НЕ нужен: bcrypt>=4.0 написан на Rust, зависимостей нет

# ── REPORTS & EXPORT ────────────────────────────────────────────────────────
reportlab==4.2.5                # PDF генерация
openpyxl==3.1.5                 # Excel (.xlsx) экспорт
python-docx==1.1.2              # Word шаблоны (DocumentEditor задания)
Pillow==11.0.0                  # Изображения: resize, convert, validate

# ── ANALYTICS / CHARTS ──────────────────────────────────────────────────────
matplotlib==3.9.3               # Графики (встраивается в PySide6 через FigureCanvas)
numpy==2.1.3                    # Зависимость matplotlib; напрямую используется в analytics_service (median, std)

# ── UTILITIES ───────────────────────────────────────────────────────────────
loguru==0.7.2                   # Структурированное логирование
# python-dateutil==2.9.0  ← ИСКЛЮЧЁН: Timeline хранит только порядок (correct_position INT),
#   не реальные даты. date_hint — TEXT-подсказка без парсинга. Библиотека не нужна.
# pytz НЕ нужен: Python 3.12 имеет встроенный zoneinfo (PEP 615)
# from zoneinfo import ZoneInfo  — использовать вместо pytz

# ── PACKAGING ───────────────────────────────────────────────────────────────
# pyinstaller==6.11.1  ← перенесён в requirements-dev.txt (инструмент сборки, не runtime)
```

### 1.2 requirements-dev.txt

```
pytest==8.3.4                   # Тест-фреймворк
pytest-qt==4.4.0                # PySide6 тестирование (QTest)
pytest-cov==6.0.0               # Покрытие тестами
pytest-mock==3.14.0             # Моки и стабы
black==24.10.0                  # Авто-форматирование кода
ruff==0.8.4                     # Быстрый линтер (заменяет flake8+isort)
mypy==1.13.0                    # Статическая типизация
# types-python-dateutil убран (python-dateutil удалён из зависимостей)
sqlalchemy[mypy]==2.0.36        # SQLAlchemy mypy плагин
pre-commit==4.0.1               # Git pre-commit хуки
pyinstaller==6.11.1             # Сборка .exe (Windows) — инструмент сборки, не runtime
cairosvg==2.7.1                 # SVG→PNG конвертация для tools/make_ico.py (dev only)
```

### 1.3 Что намеренно НЕ включено и почему

| Библиотека     | Почему не берём                            |
| -------------- | ------------------------------------------ |
| PyQt6          | PySide6 — официальный Qt, LGPL без royalty |
| Django/FastAPI | Офлайн-приложение, не нужен web-сервер     |
| Qt-Material    | Вся тема своя — полный контроль            |
| pydantic       | Используем SQLAlchemy dataclasses          |
| aiohttp        | Нет сетевых запросов по условию задачи     |
| redis          | Нет сервера, кэш — in-memory dict          |
| celery         | Нет очередей, тяжёлые задачи — QThread     |

---

## 2. КОНФИГУРАЦИЯ ПРИЛОЖЕНИЯ

### 2.1 Файловая структура данных

```
%APPDATA%/EduCase/          (Windows: C:\Users\<user>\AppData\Roaming\EduCase)
├── educase.db              # Главная БД (SQLite)
├── config.json             # Пользовательские настройки
├── logs/
│   ├── app_2026-03-04.log  # Ежедневные логи (ротация 7 дней)
│   └── errors.log          # Только ошибки (ERROR+)
├── media/
│   ├── covers/             # Обложки кейсов (PNG, max 2MB, 800x450)
│   ├── task_images/        # Изображения для заданий (PNG/JPG, max 5MB)
│   ├── avatars/            # Аватары пользователей (PNG, 256x256, max 512KB)
│   └── exports/            # Временные файлы экспорта (PDF, XLSX)
└── backups/
    ├── backup_2026-03-01.db
    └── backup_2026-03-02.db   # Авто-бэкап при запуске (хранить 7)
```

### 2.2 config.py — полная реализация

```python
# config.py
import json, os
from dataclasses import dataclass, asdict, fields  # fields(cls) используется в AppConfig.load()
from pathlib import Path
from typing import Literal

APP_NAME    = "EduCase"
APP_VERSION = "1.0.0"  # версия продукта (2.0 — версия документации)
APP_AUTHOR  = "ВМедА им. С.М. Кирова"

if os.name == 'nt':
    DATA_DIR = Path(os.environ["APPDATA"]) / APP_NAME
else:
    DATA_DIR = Path.home() / f".{APP_NAME.lower()}"

DB_PATH     = DATA_DIR / "educase.db"
LOG_DIR     = DATA_DIR / "logs"
MEDIA_DIR   = DATA_DIR / "media"
BACKUP_DIR  = DATA_DIR / "backups"
CONFIG_PATH = DATA_DIR / "config.json"

def _init_dirs() -> None:
    # Вызывается в main.py ДО build_container(). В тестах НЕ вызывать.
    for d in [DATA_DIR, LOG_DIR, MEDIA_DIR, BACKUP_DIR,
              MEDIA_DIR/"covers", MEDIA_DIR/"task_images",
              MEDIA_DIR/"avatars", MEDIA_DIR/"exports"]:
        d.mkdir(parents=True, exist_ok=True)

MEDIA_LIMITS = {
    "cover":      {"max_bytes": 2*1024*1024, "formats": ["png","jpg","jpeg"]},
    "task_image": {"max_bytes": 5*1024*1024, "formats": ["png","jpg","jpeg","gif"]},
    "avatar":     {"max_bytes": 512*1024,    "formats": ["png","jpg","jpeg"]},
}

MAX_LOGIN_ATTEMPTS   = 5
LOGIN_LOCKOUT_SECONDS = 300

@dataclass
class AppConfig:
    theme: Literal["light","dark"] = "light"
    accent_color: str   = "#0078D4"
    font_size_base: int = 13
    sidebar_expanded: bool = True
    auto_backup: bool  = True
    backup_count: int  = 7
    language: str      = "ru"
    window_width: int  = 1280
    window_height: int = 800
    window_maximized: bool  = False
    animations_enabled: bool = True
    animation_speed: float  = 1.0   # 0.5=быстрее, 2.0=медленнее

    @classmethod
    def load(cls) -> "AppConfig":
        try:
            raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            # ✅ фильтруем лишние ключи — защита от несовместимости версий
            valid = {f.name for f in fields(cls)}
            return cls(**{k: v for k, v in raw.items() if k in valid})
        except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
            return cls()  # fallback на дефолты (FileNotFoundError при первом запуске)
        # ✅ Значения не валидируются — font_size<0 или невалидный hex не крашат при load,
        #    обнаруживаются при применении темы (stylesheet.py clamps значения)

    def save(self) -> None:
        CONFIG_PATH.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

CONFIG = AppConfig.load()
```

---

## 3. БАЗА ДАННЫХ — ПОЛНАЯ СХЕМА

### 3.1 SQLite-настройки при подключении

```python
# core/database.py
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool            # ← новый conn на каждый запрос, thread-safe
from config import DB_PATH                      # путь к файлу БД

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    # ✅ NullPool: новое соединение на каждый запрос
    #    Безопаснее StaticPool при QThread Workers (нет разделяемого conn)
    connect_args={"check_same_thread": False},
    poolclass=NullPool,
    echo=False,
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, _):
    # ✅ ПРАВИЛЬНО: через cursor (dbapi_conn — это sqlite3.Connection)
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")      # Write-Ahead Logging
    cursor.execute("PRAGMA foreign_keys=ON")        # Каскадные удаления
    cursor.execute("PRAGMA synchronous=NORMAL")     # Баланс безопасность/скорость
    cursor.execute("PRAGMA cache_size=-32000")      # 32MB page cache
    cursor.execute("PRAGMA temp_store=MEMORY")      # Временные таблицы в RAM
    cursor.execute("PRAGMA busy_timeout=5000")      # Ждать 5с при блокировке
    cursor.close()

Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def run_migrations() -> None:
    """Обёртка над Alembic upgrade(head). Вызывается из main.py при старте."""
    from alembic.config import Config
    from alembic import command
    from config import DB_PATH
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent
    cfg = Config(str(BASE_DIR / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{DB_PATH}")
    command.upgrade(cfg, "head")
```

### 3.2 Полная схема всех таблиц

```sql
-- ПОЛЬЗОВАТЕЛИ И ДОСТУП

CREATE TABLE roles (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    permissions  TEXT NOT NULL DEFAULT '{}'
);

-- ✅ ИСПРАВЛЕН порядок: users → groups (была circular FK).
-- users.group_id: целое без REFERENCES (SQLite не позволяет ALTER ADD с FK).
-- Связь group поддерживается SQLAlchemy relationship + app-level check.
CREATE TABLE users (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    username       TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,  -- bcrypt: всегда 60 символов ($2b$12$...)
    full_name      TEXT NOT NULL,
    role_id        INTEGER NOT NULL REFERENCES roles(id),
    group_id       INTEGER,          -- мягкая FK → groups.id (без DDL constraint)
    avatar_path    TEXT,
    is_active      INTEGER NOT NULL DEFAULT 1,
    last_login_at  TEXT,             -- обновляется AuthService при успешном входе
    login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until   TEXT,             -- NULL = не заблокирован
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_users_role     ON users(role_id);
CREATE INDEX idx_users_group    ON users(group_id);
CREATE INDEX idx_users_username ON users(username);
CREATE TRIGGER users_updated_at AFTER UPDATE ON users BEGIN
    UPDATE users SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- groups ПОСЛЕ users
CREATE TABLE groups (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT,
    teacher_id  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),  -- ✅ добавлено для аудита изменений
    is_active   INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX idx_groups_teacher  ON groups(teacher_id);
CREATE INDEX idx_groups_active   ON groups(is_active);
CREATE TRIGGER groups_updated_at AFTER UPDATE ON groups BEGIN
    UPDATE groups SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- УЧЕБНЫЙ КОНТЕНТ

CREATE TABLE disciplines (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT,
    icon_name   TEXT NOT NULL DEFAULT 'book',
    color_hex   TEXT NOT NULL DEFAULT '#0078D4',
    order_index INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE topics (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    discipline_id INTEGER NOT NULL REFERENCES disciplines(id) ON DELETE CASCADE,
    name          TEXT NOT NULL,
    order_index   INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX idx_topics_discipline ON topics(discipline_id);

CREATE TABLE cases (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id      INTEGER NOT NULL REFERENCES topics(id) ON DELETE RESTRICT,
    author_id     INTEGER REFERENCES users(id) ON DELETE SET NULL, -- ✅ nullable: кейс не пропадает при удалении преподавателя
    title         TEXT NOT NULL,
    description   TEXT,
    cover_path    TEXT,
    status        TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','review','published','archived')),
    time_limit_min INTEGER,  -- NULL = без ограничения времени; >0 = лимит в минутах
    max_attempts  INTEGER,  -- NULL = неограниченное количество попыток
    passing_score INTEGER NOT NULL DEFAULT 60,  -- % (0–100); grade_map в settings хранит пороги как доли (0.0–1.0)
    settings      TEXT NOT NULL DEFAULT '{"grade_map":{"5":0.9,"4":0.75,"3":0.6},"show_answers":true,"allow_retry":true}',
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT NOT NULL DEFAULT (datetime('now')),
    published_at  TEXT
);
CREATE INDEX idx_cases_topic  ON cases(topic_id);
CREATE INDEX idx_cases_author ON cases(author_id);
CREATE INDEX idx_cases_status ON cases(status);
-- ✅ CHECK constraints добавлены inline в CREATE TABLE (см. status/level/module_type выше)
-- ⚠️ SQLite НЕ поддерживает ALTER TABLE ADD CONSTRAINT — только inline при CREATE TABLE
-- tasks.task_type: не CHECK-ограничен в DDL; валидируется через TASK_TYPES константу в TaskService (12 значений)
CREATE TRIGGER cases_updated_at AFTER UPDATE ON cases BEGIN
    UPDATE cases SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TABLE case_groups (
    case_id     INTEGER REFERENCES cases(id) ON DELETE CASCADE,
    group_id    INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    assigned_at TEXT NOT NULL DEFAULT (datetime('now')),
    deadline    TEXT,  -- ✅ дедлайн для конкретной группы (NULL = без дедлайна)
    PRIMARY KEY (case_id, group_id)
);
CREATE INDEX idx_case_groups_group ON case_groups(group_id); -- ✅ поиск по группе

CREATE TABLE modules (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id     INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL DEFAULT 0,
    module_type TEXT NOT NULL DEFAULT 'linear' CHECK (module_type IN ('linear','branching'))
);
CREATE INDEX idx_modules_case ON modules(case_id);
CREATE UNIQUE INDEX idx_modules_order ON modules(case_id, order_index); -- без дублей порядка

-- ЗАДАНИЯ (все 12 типов + подтаблицы)

CREATE TABLE tasks (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id      INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    title          TEXT NOT NULL,
    body           TEXT,                  -- NULL допустим; плеер пропускает QTextBrowser если body IS NULL
    task_type      TEXT NOT NULL,
    order_index    INTEGER NOT NULL DEFAULT 0,
    max_score      REAL NOT NULL DEFAULT 10.0,     -- ✅ REAL (дробные баллы)
    partial_credit INTEGER NOT NULL DEFAULT 0,
    penalty_score  REAL NOT NULL DEFAULT 0.0,        -- ✅ REAL
    hint_text      TEXT,  -- подсказка ДО ответа (по кнопке 💡 в плеере)
    explanation    TEXT,  -- объяснение ПОСЛЕ ответа (в FeedbackPanel)
    media_id       INTEGER REFERENCES media_files(id) ON DELETE SET NULL,
    -- ✅ FK на media_files: SQLite проверяет FK при INSERT, не при DDL,
    --    поэтому форвард-ссылка работает. В migration-скрипте media_files
    --    создаётся в 002_content_schema.py РАНЬШЕ tasks (см. порядок миграций).
    settings       TEXT NOT NULL DEFAULT '{}',
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_tasks_module ON tasks(module_id);
CREATE INDEX idx_tasks_type   ON tasks(task_type);
CREATE UNIQUE INDEX idx_tasks_order ON tasks(module_id, order_index);

CREATE TABLE task_options (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id     INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    text        TEXT NOT NULL,
    is_correct  INTEGER NOT NULL DEFAULT 0,
    order_index INTEGER NOT NULL DEFAULT 0,
    feedback    TEXT
);

CREATE TABLE task_keywords (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id       INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    keyword       TEXT NOT NULL,
    synonyms      TEXT NOT NULL DEFAULT '[]',
    action_result TEXT,
    score_value   REAL NOT NULL DEFAULT 0.0,   -- REAL: дробные баллы за ключевое слово
    case_sensitive INTEGER NOT NULL DEFAULT 0
    -- ✅ сравнение выполняется в Python: keyword.lower() in answer.lower() (NOT SQLite LIKE)
);

CREATE TABLE task_form_fields (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id       INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    field_key     TEXT NOT NULL,
    field_label   TEXT NOT NULL,
    field_type    TEXT NOT NULL DEFAULT 'text',
    correct_value TEXT,
    options_json  TEXT,
    validation_re TEXT,
    is_required   INTEGER NOT NULL DEFAULT 1,
    order_index   INTEGER NOT NULL DEFAULT 0,
    score_value   REAL NOT NULL DEFAULT 1.0    -- REAL: вес поля в итоговом балле
);

CREATE TABLE task_pairs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id     INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    left_text   TEXT NOT NULL,
    right_text  TEXT NOT NULL,
    order_index INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE task_order_items (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id       INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    text          TEXT NOT NULL,
    correct_order INTEGER NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE task_timeline_events (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id          INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    event_text       TEXT NOT NULL,
    correct_position INTEGER NOT NULL,
    date_hint        TEXT
);

CREATE TABLE task_image_zones (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id    INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    zone_label TEXT NOT NULL,
    x          REAL NOT NULL,
    y          REAL NOT NULL,
    width      REAL NOT NULL,
    height     REAL NOT NULL,
    is_correct INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE task_table_cells (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id       INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    row_index     INTEGER NOT NULL,
    col_index     INTEGER NOT NULL,
    header_text   TEXT,
    correct_value TEXT,
    is_editable   INTEGER NOT NULL DEFAULT 1,
    cell_type     TEXT NOT NULL DEFAULT 'text',
    UNIQUE (task_id, row_index, col_index)  -- ✅ не может быть двух ячеек в одной позиции
);

-- ✅ индексы на все подтаблицы заданий (task_id — частый JOIN-ключ)
-- объявлены ПОСЛЕ всех CREATE TABLE подтаблиц (SQLite требует таблицу до индекса)
CREATE INDEX idx_task_options_task   ON task_options(task_id);
CREATE INDEX idx_task_keywords_task  ON task_keywords(task_id);
CREATE INDEX idx_task_fields_task    ON task_form_fields(task_id);
CREATE INDEX idx_task_pairs_task     ON task_pairs(task_id);
CREATE INDEX idx_task_order_task     ON task_order_items(task_id);
CREATE INDEX idx_task_timeline_task  ON task_timeline_events(task_id);
CREATE INDEX idx_task_zones_task     ON task_image_zones(task_id);
CREATE INDEX idx_task_cells_task     ON task_table_cells(task_id);

-- ВЕТВЯЩИЕСЯ СЦЕНАРИИ

CREATE TABLE scenario_nodes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    -- ✅ ИСПРАВЛЕНО: узел принадлежит MODULE, не одному заданию
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    task_id   INTEGER REFERENCES tasks(id) ON DELETE SET NULL,  -- nullable
    node_type TEXT NOT NULL,
    title     TEXT NOT NULL,
    content   TEXT,
    x_pos     REAL NOT NULL DEFAULT 0,
    y_pos     REAL NOT NULL DEFAULT 0,
    color_hex TEXT     -- NULL = цвет определяется node_type (START→синий, КОНЕЦ→тёмный)
);

CREATE TABLE scenario_edges (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node_id INTEGER NOT NULL REFERENCES scenario_nodes(id) ON DELETE CASCADE,
    to_node_id   INTEGER NOT NULL REFERENCES scenario_nodes(id) ON DELETE CASCADE,
    label        TEXT,
    condition    TEXT,    -- JSON: {"option_id":3} | {"keyword":"hepatitis"} | null (безусловное)
    score_delta  REAL NOT NULL DEFAULT 0.0,    -- REAL: бонус/штраф при переходе
    is_correct   INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX idx_scenario_nodes_module ON scenario_nodes(module_id);
CREATE INDEX idx_scenario_nodes_task   ON scenario_nodes(task_id);
CREATE INDEX idx_scenario_edges_from ON scenario_edges(from_node_id);
CREATE INDEX idx_scenario_edges_to   ON scenario_edges(to_node_id);

-- ПОПЫТКИ СТУДЕНТОВ

CREATE TABLE attempts (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    case_id           INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    attempt_num       INTEGER NOT NULL DEFAULT 1,
    -- AttemptService.start(): SELECT COALESCE(MAX(attempt_num),0)+1 ... WHERE user_id=? AND case_id=?
    -- Race-safe: SQLite WAL Writer Lock + UNIQUE idx_attempts_active предотвращает двойную попытку
    status            TEXT NOT NULL DEFAULT 'in_progress' CHECK (status IN ('in_progress','completed','abandoned')),
    total_score       REAL NOT NULL DEFAULT 0.0,
    max_score         REAL NOT NULL DEFAULT 0.0,
    started_at        TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at       TEXT,
    duration_sec      INTEGER,
    -- finish(): int((datetime.now() - started_at).total_seconds())
    current_module_id INTEGER REFERENCES modules(id),
    current_task_id   INTEGER REFERENCES tasks(id)
);
CREATE INDEX idx_attempts_user   ON attempts(user_id);
CREATE INDEX idx_attempts_case   ON attempts(case_id);
CREATE INDEX idx_attempts_status ON attempts(status);
CREATE UNIQUE INDEX idx_attempts_active
    ON attempts(user_id, case_id) WHERE status = 'in_progress';

CREATE TABLE attempt_answers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id      INTEGER NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
    task_id         INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    answer_data     TEXT NOT NULL DEFAULT '{}',
    score_received  REAL NOT NULL DEFAULT 0.0,      -- ✅ REAL
    max_score       REAL NOT NULL DEFAULT 0.0,        -- ✅ REAL
    is_correct      INTEGER,
    grading_details TEXT,
    answered_at     TEXT NOT NULL DEFAULT (datetime('now')),
    time_spent_sec  INTEGER
);
CREATE INDEX idx_answers_attempt ON attempt_answers(attempt_id);
-- ✅ один ответ на задание за попытку (повторная отправка = UPDATE, не INSERT)
CREATE UNIQUE INDEX idx_answers_unique ON attempt_answers(attempt_id, task_id);
CREATE INDEX idx_answers_task    ON attempt_answers(task_id);

CREATE TABLE attempt_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
    action     TEXT NOT NULL,
    data       TEXT,
    timestamp  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_attempt_log_attempt ON attempt_log(attempt_id); -- ✅ добавлен

-- МЕДИАФАЙЛЫ И СИСТЕМНЫЕ ТАБЛИЦЫ

CREATE TABLE media_files (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    filename    TEXT NOT NULL,
    stored_name TEXT NOT NULL UNIQUE,
    file_path   TEXT NOT NULL,
    thumb_path  TEXT,              -- ✅ путь к миниатюре (NULL если не изображение)
    mime_type   TEXT NOT NULL,
    file_size   INTEGER NOT NULL,
    width       INTEGER,           -- px (NULL для не-изображений)
    height      INTEGER,           -- px
    media_type  TEXT NOT NULL CHECK (media_type IN ('cover','task_image','avatar','export')),
    uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE system_settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TRIGGER system_settings_updated_at AFTER UPDATE ON system_settings BEGIN
    UPDATE system_settings SET updated_at = datetime('now') WHERE key = NEW.key;
END;

CREATE TABLE system_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    level       TEXT NOT NULL DEFAULT 'INFO' CHECK (level IN ('INFO','WARNING','ERROR','AUDIT')),
    action      TEXT NOT NULL,
    entity_type TEXT,
    entity_id   INTEGER,
    details     TEXT,
    timestamp   TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_syslog_user  ON system_logs(user_id);
CREATE INDEX idx_syslog_level ON system_logs(level);
CREATE INDEX idx_syslog_time  ON system_logs(timestamp);

-- SEED: роли и дисциплины по умолчанию
INSERT INTO roles (name, display_name, permissions) VALUES
('student',  'Студент',         '{"can_take_cases":true}'),
('teacher',  'Преподаватель',   '{"can_create_case":true,"can_manage_groups":true,"can_view_analytics":true}'),
('admin',    'Администратор',   '{"all":true}');

-- ✅ Дефолтный admin (пароль меняется при первом входе)
-- ⚠️ НЕ вставлять PLACEHOLDER напрямую — bcrypt.checkpw упадёт с ValueError!
-- seed.py генерирует корректный хэш программно:
--   hash = bcrypt.hashpw(b'Admin1234', bcrypt.gensalt(rounds=12)).decode()
--   INSERT INTO users ... VALUES ('admin', hash, ...)
-- Дефолтный пароль при первом запуске: Admin1234 (сменить сразу после установки)

INSERT INTO disciplines (name, icon_name, color_hex, order_index) VALUES
('Военная эпидемиология', 'shield_medical', '#0078D4', 1),
('Общая эпидемиология',   'virus',          '#107C10', 2),
('Инфекционные болезни',  'bacteria',       '#C75300', 3);
```

### 3.3 DB Maintenance (фоновый поток при запуске)

```python
# core/db_maintenance.py
from sqlalchemy import text
from config import DB_PATH
from core.database import engine

def run_maintenance():
    # ✅ VACUUM → нужен AUTOCOMMIT (нельзя внутри транзакции)
    # ✅ SQLAlchemy 2.0: execution_options задаём на engine, не на connect()
    ac_engine = engine.execution_options(isolation_level="AUTOCOMMIT")
    with ac_engine.connect() as conn:
        if DB_PATH.stat().st_size > 50 * 1024 * 1024:
            conn.execute(text("PRAGMA wal_checkpoint(FULL)"))
            conn.execute(text("VACUUM"))
    # Обычная очистка — в отдельной транзакции (engine.begin() — auto-commit)
    with engine.begin() as conn:
        conn.execute(text(
            "DELETE FROM system_logs WHERE timestamp < datetime('now', '-90 days')"
        ))
        conn.execute(text(
            "UPDATE attempts SET status='abandoned' WHERE status='in_progress' "
            "AND started_at < datetime('now', '-30 days')"
        ))
        # ✅ НЕ вызываем conn.commit() — engine.begin() делает это автоматически
```

---

## 4. АРХИТЕКТУРА — ПОЛНАЯ СТРУКТУРА ПРОЕКТА

```
educase/
│
├── main.py                         # Точка входа: QApplication + LoginWindow
├── app.py                          # Singleton App: CONFIG, DB, current_user
├── config.py                       # AppConfig, DATA_DIR, MEDIA_LIMITS
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml           # [project] python_requires = ">=3.12"
│                            # [tool.black] line-length=100
│                            # [tool.ruff] select=["E","F","I","UP"] line-length=100
│                            # [tool.mypy] strict=true plugins=["sqlalchemy.ext.mypy.plugin"]
│                            # [tool.pytest.ini_options] testpaths=["tests"] addopts="--tb=short -q"
├── alembic.ini              # sqlalchemy.url = %(DB_PATH)s — подставляется динамически
│                            # в migrations/env.py: config.set_main_option("sqlalchemy.url", f"sqlite:///{DB_PATH}")
│
├── core/
│   ├── database.py                 # engine, Session, pragma
│   ├── db_maintenance.py           # VACUUM, cleanup
│   ├── exceptions.py               # Иерархия:
│   │                                #   AppError(Exception)
│   │                                #   ├─ AuthError (неверный пароль / заблокирован)
│   │                                #   ├─ PermissionError (нет прав)
│   │                                #   ├─ NotFoundError (объект не найден в БД)
│   │                                #   ├─ ValidationError (неверные данные формы)
│   │                                #   └─ MediaError (файл слишком большой / неверный тип)
│   ├── event_bus.py                # Qt EventBus singleton
│   ├── di_container.py             # простой DI (регистрация + resolve)
│   ├── thread_pool.py              # Worker + run_async
│   ├── validators.py               # validate_username: [a-zA-Z0-9_], 3–30 символов
│   │                                # validate_password: ≥8 символов, ≥1 цифра
│   │                                # validate_image(path, media_type): size+MIME через Pillow
│   └── logger.py                   # loguru setup + DB sink
│
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_initial_schema.py      # users, roles, groups
│       │                              # disciplines, topics (нужны до кейсов)
│       ├── 002_content_schema.py      # cases, modules, tasks, scenarios, attempts, media
│       └── 003_system_settings.py
│
├── models/
│   ├── __init__.py
│   ├── base.py                     # Base, TimestampMixin
│   ├── user.py                     # User, Role, Group
│   ├── content.py                  # Discipline, Topic, Case, CaseGroup, Module
│   ├── task.py                     # Task + 8 подтаблиц (options/keywords/form_fields/pairs/order_items/timeline/image_zones/table_cells)
│   ├── scenario.py                 # ScenarioNode, ScenarioEdge
│   ├── attempt.py                  # Attempt, AttemptAnswer, AttemptLog
│   ├── media.py                    # MediaFile
│   └── system.py                   # SystemSetting, SystemLog
│
├── repositories/
│   ├── base.py                     # BaseRepo[T]: get, get_all, create, update, delete
│   ├── user_repo.py
│   ├── group_repo.py
│   ├── case_repo.py
│   ├── module_repo.py              # ← добавлен: reorder, get_by_case
│   ├── task_repo.py
│   ├── scenario_repo.py
│   ├── attempt_repo.py
│   ├── media_repo.py
│   └── analytics_repo.py           # сложные SQL для аналитики
│
├── services/
│   ├── auth_service.py             # login, logout, current_user, check_permission
│   ├── user_service.py             # create, update_profile, change_password
│   ├── group_service.py            # create_group, add_member, remove_member
│   ├── case_service.py             # CRUD + publish + duplicate + export_to_json
│   │                                # export_to_json(case_id) → dict (V3 импорт/экспорт)
│   │                                # publish() валидирует: ≥1 модуль, каждый модуль ≥1 задание,
│   │                                #   branching-модуль → валидный граф (≥1 START, ≥1 END),
│   │                                #   passing_score ∈ [1,100], у кейса есть topic_id
│   ├── module_service.py           # CRUD + reorder
│   ├── task_service.py             # CRUD 12 типов
│   ├── media_service.py            # upload, validate, resize, delete
│   ├── grader_service.py           # grade_answer для всех типов
│   ├── scenario_service.py         # traverse, get_next_node
│   ├── attempt_service.py          # start, resume, save_answer, finish, abandon, pause, get_progress
│   │                                # start(): если attempt_num > case.max_attempts → raise ValidationError
│   │                                # resume(): если нет активной попытки → raise NotFoundError
│   ├── analytics_service.py        # методы и возвращаемые типы:
│   │                                #   heatmap(case_id,group_id) → list[list[float]]  # [student][task]=%
│   │                                #   score_distribution(case_id) → dict[str,int]  # {"0-10":3,...}
│   │                                #   weak_tasks(case_id) → list[dict]  # [{id,title,avg_score}]
│   │                                #   group_summary(group_id) → dict  # {avg,median,best,worst}
│   ├── export_service.py           # PDF + Excel
│   └── backup_service.py           # create, restore, list
│
├── ui/
│   ├── styles/
│   │   ├── theme.py                # ColorTokens, SpacingTokens, RadiusTokens, ANIM
│   │   ├── stylesheet.py           # Глобальный QSS
│   │   ├── animations.py           # fade_in/out, slide, shake, stagger, sidebar_expand
│   │   └── icons.py                # SVGIcon, get_icon(), 55 иконок inline
│   │
│   ├── components/
│   │   ├── sidebar.py
│   │   ├── topbar.py
│   │   ├── card.py
│   │   ├── case_card.py
│   │   ├── stat_card.py
│   │   ├── badge.py
│   │   ├── avatar.py
│   │   ├── progress_ring.py
│   │   ├── progress_bar.py
│   │   ├── toast.py
│   │   ├── dialog.py
│   │   ├── table_view.py
│   │   ├── search_bar.py
│   │   ├── tag.py
│   │   ├── empty_state.py
│   │   ├── loading_overlay.py
│   │   ├── rich_text_editor.py
│   │   ├── image_picker.py
│   │   ├── score_badge.py
│   │   ├── accordion.py
│   │   ├── stepper.py
│   │   └── color_picker.py
│   │
│   ├── windows/
│   │   ├── login_window.py
│   │   └── main_window.py
│   │
│   ├── screens/
│   │   ├── student/
│   │   │   ├── dashboard.py        # S-1
│   │   │   ├── my_cases.py         # S-2
│   │   │   ├── case_player.py      # S-3
│   │   │   ├── case_result.py      # S-4
│   │   │   ├── my_results.py       # S-5
│   │   │   └── profile.py          # S-6
│   │   ├── teacher/
│   │   │   ├── dashboard.py        # T-1
│   │   │   ├── my_cases.py         # T-2
│   │   │   ├── case_editor.py      # T-3
│   │   │   ├── analytics.py        # T-6
│   │   │   ├── groups.py           # T-7
│   │   │   └── group_detail.py     # T-8
│   │   └── admin/
│   │       ├── dashboard.py        # A-1
│   │       ├── users.py            # A-2
│   │       ├── user_editor.py      # A-3
│   │       ├── system.py           # A-4
│   │       └── logs.py             # A-5
│   │
│   ├── task_constructor/           # T-4
│   │   ├── constructor_dialog.py
│   │   ├── type_selector.py
│   │   ├── preview_panel.py
│   │   ├── base_editor.py
│   │   ├── editors/                # 12 редакторов типов заданий
│   │   │   ├── editor_single_choice.py
│   │   │   ├── editor_multi_choice.py
│   │   │   ├── editor_text_input.py
│   │   │   ├── editor_form_fill.py
│   │   │   ├── editor_ordering.py
│   │   │   ├── editor_matching.py
│   │   │   ├── editor_calculation.py
│   │   │   ├── editor_image_annotation.py
│   │   │   ├── editor_branching.py
│   │   │   ├── editor_document.py
│   │   │   ├── editor_timeline.py
│   │   │   └── editor_table_input.py
│   │   └── scenario_builder/       # T-5
│   │       ├── graph_scene.py
│   │       ├── graph_view.py
│   │       ├── node_item.py
│   │       └── edge_item.py
│   │
│   └── task_widgets/               # 12 виджетов для студента
│       ├── base_task_widget.py
│       ├── widget_single_choice.py
│       ├── widget_multi_choice.py
│       ├── widget_text_input.py
│       ├── widget_form_fill.py
│       ├── widget_ordering.py
│       ├── widget_matching.py
│       ├── widget_calculation.py
│       ├── widget_image_annotation.py
│       ├── widget_branching.py
│       ├── widget_document_editor.py
│       ├── widget_timeline.py
│       └── widget_table_input.py
│
├── presenters/
│   ├── base_presenter.py
│   ├── auth_presenter.py
│   ├── student/            # 6 презентеров: dashboard, my_cases, case_player,
│   │                        #   case_result, my_results, profile
│   ├── teacher/            # 6 презентеров: dashboard, my_cases, case_editor,
│   │                        #   analytics, groups, group_detail
│   └── admin/              # 5 презентеров: dashboard, users, user_editor,
│                            #   system, logs
│
├── assets/
│   ├── fonts/SegoeUIVariable.ttf
│   ├── icon.ico                    # Мульти-размер ICO: 256/128/64/32/16px (генерируется tools/make_ico.py)
│   ├── icon_master.svg             # Мастер-иконка 256×256 viewBox (источник для ICO)
│   └── doc_templates/
│       ├── emergency_notice.docx
│       ├── lab_referral.docx
│       └── outbreak_act.docx
│
├── seed.py                         # Начальные данные: роли, admin, 3 дисциплины, тестовые пользователи
│                                   # Запускается через: python -m seed  (или в alembic post-migrate hook)
├── tools/
│   └── make_ico.py                 # Генерация assets/icon.ico из SVG (dev, cairosvg+Pillow)
│
└── tests/
    ├── conftest.py             # fixtures: in_memory_db, session, container, seed_users
    │                            # in_memory_db: переопределяет DB_PATH = ":memory:"
    │                            # + StaticPool с check_same_thread=False → все запросы
│                            #   в тесте делят ОДНО соединение к :memory: (NullPool
│                            #   создавал бы новую пустую БД на каждый вызов Session())
    ├── unit/
    │   ├── test_auth.py        # login/lockout/session
    │   ├── test_grader.py      # все 12 типов × верный/неверный/частичный
    │   ├── test_scenario.py    # обход дерева, тупики, циклы
    │   ├── test_attempt.py     # start/resume/finish/abandon
    │   ├── test_analytics.py   # heatmap, score distribution
    │   └── test_export.py      # PDF/Excel без ошибок
    └── ui/
        ├── test_login.py       # логин / ошибка / блокировка
        ├── test_case_player.py # открыть → ответить → результат
        └── test_constructor.py # создать задание каждого типа
```

### 4.0 app.py и main.py — последовательность запуска

> ⚠️ **Актуальная реализация main.py** — в **§15.4** (включает SplashScreen, анимации, гарантию 2500ms).
> Ниже — упрощённая схема для понимания структуры, **не для копирования**.

```python
# main.py — СХЕМА (полная реализация в §15.4)
import time, sys
# from PySide6.QtWidgets import QApplication
# from PySide6.QtGui     import QIcon, QFontDatabase
# from PySide6.QtCore    import QTimer
# from core.di_container import build_container
# from core.database     import run_migrations
# from core.thread_pool  import run_async
# from core.db_maintenance import run_maintenance
# from ui.windows.login_window  import LoginWindow
# from ui.windows.splash_window import SplashScreen
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("EduCase")
    app.setApplicationVersion("1.0.0")
    app.setWindowIcon(QIcon("assets/icon.ico"))

    # 0. Директории данных
    from config import _init_dirs; _init_dirs()

    # 1. Шрифты
    QFontDatabase.addApplicationFont("assets/fonts/SegoeUIVariable.ttf")

    # 2. SplashScreen (полная версия с анимацией — см. §15)
    splash = SplashScreen(); splash.start()
    t_start = time.monotonic()  # ✅ фиксируем время ПОСЛЕ показа splash
    app.processEvents()

    # 3. Миграции (полная реализация: core/database.py → run_migrations(), см. §3.1)
    run_migrations(); app.processEvents()

    # 4. Фоновое обслуживание БД
    QTimer.singleShot(3000, lambda: run_async(run_maintenance))

    # 5. DI-контейнер
    container = build_container()

    # 6. LoginWindow через splash.finish() — см. §15.4
    login = LoginWindow(container)
    elapsed_ms = int((time.monotonic() - t_start) * 1000)
    delay_ms   = max(0, 2500 - elapsed_ms)   # полная реализация — см. §15.4
    QTimer.singleShot(delay_ms, lambda: splash.finish(login))

    sys.exit(app.exec())

# app.py — модульные переменные (не класс — mypy не терпит None без default_factory)
current_user = None   # type: User | None
# ✅ Single-session: приложение открывает только одно главное окно — конфликтов нет.
# Для multi-window потребовался бы context-var или per-window state.
config: AppConfig = CONFIG
container    = None   # type: Container | None

def get_session():
    # Всегда использовать через with: with get_session() as s: ...
    return Session()
```

### 4.1 EventBus

```python
# core/event_bus.py
from PySide6.QtCore import QObject, Signal

class EventBus(QObject):
    user_logged_in   = Signal(object)   # User
    user_logged_out  = Signal()
    navigate_to      = Signal(str, object)  # screen_name, kwargs (dict не Q_TYPE)
    show_toast       = Signal(str, str)  # message, level ("success"/"error"/"info"/"warning")
    case_published   = Signal(int)      # case_id
    attempt_finished = Signal(int)      # attempt_id
    user_updated     = Signal(int)      # user_id

    _instance = None
    @classmethod
    def instance(cls) -> "EventBus":
        # ✅ вызывается только из main-потока при старте — не thread-safe,
        #    но это норма для Qt: QObject нельзя создавать вне main-потока
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

bus = EventBus.instance()
# ⚠️ Этот вызов происходит при import event_bus — QApplication должен быть создан ДО импорта.
#    В тестах: создать QApplication в conftest.py до любого импорта UI-модулей.
```

### 4.2 DI Container — реализация

```python
# core/di_container.py
from dataclasses import dataclass

@dataclass
class Container:
    """Простой DI: все зависимости собираются здесь один раз при старте."""
    # Repositories
    user_repo:     UserRepository | None     = None
    group_repo:    GroupRepository | None    = None
    case_repo:     CaseRepository | None     = None
    module_repo:   ModuleRepository | None   = None
    task_repo:     TaskRepository | None     = None
    scenario_repo: ScenarioRepository | None = None
    attempt_repo:  AttemptRepository | None  = None
    media_repo:    MediaRepository | None    = None
    analytics_repo: AnalyticsRepository | None = None
    # Services
    auth_service:     AuthService | None     = None
    user_service:     UserService | None     = None
    group_service:    GroupService | None    = None
    case_service:     CaseService | None     = None
    module_service:   ModuleService | None   = None
    task_service:     TaskService | None     = None
    media_service:    MediaService | None    = None
    grader_service:   GraderService | None   = None
    scenario_service: ScenarioService | None = None
    attempt_service:  AttemptService | None  = None
    analytics_service: AnalyticsService | None = None
    export_service:   ExportService | None   = None
    backup_service:   BackupService | None   = None

def build_container() -> Container:
    c = Container()
    # Все репозитории и сервисы — STATELESS синглтоны.
    # Состояние (current_user, config) хранится в app.py, НЕ в сервисах.
    # Repos (получают новую session при каждом вызове через Session())
    c.user_repo     = UserRepository()
    c.group_repo    = GroupRepository()
    c.case_repo     = CaseRepository()
    c.task_repo     = TaskRepository()
    c.scenario_repo = ScenarioRepository()
    c.attempt_repo  = AttemptRepository()
    c.media_repo    = MediaRepository()
    c.analytics_repo = AnalyticsRepository()
    c.module_repo    = ModuleRepository()      # ✅ все repos объявлены до services
    # Services
    c.auth_service     = AuthService(c.user_repo)
    c.user_service     = UserService(c.user_repo, c.media_repo)
    c.group_service    = GroupService(c.group_repo, c.user_repo)
    c.case_service     = CaseService(c.case_repo, c.media_repo)
    c.module_service = ModuleService(c.module_repo)
    c.task_service     = TaskService(c.task_repo, c.media_repo)
    c.media_service    = MediaService(c.media_repo)
    c.grader_service   = GraderService(c.task_repo)
    c.scenario_service = ScenarioService(c.scenario_repo)
    c.attempt_service  = AttemptService(
        c.attempt_repo, c.grader_service, c.scenario_service)
    c.analytics_service = AnalyticsService(c.analytics_repo)
    c.export_service   = ExportService(c.analytics_service, c.attempt_repo)
    c.backup_service   = BackupService()
    return c
```

### 4.3 Threading-модель

**NullPool + WAL:** каждый Worker создаёт новое SQLite-соединение.
WAL разрешает N читателей + 1 писатель одновременно. busy_timeout=5000ms уже установлен.
**Правило сессий:** каждая DB-операция в Worker — в отдельном `with Session() as s:` блоке.
Утечка сессии = утечка файлового дескриптора SQLite → зависание следующего Writer'а.

```python
# core/thread_pool.py
from PySide6.QtCore import QRunnable, QThreadPool, QObject, Signal
from typing import Callable

class _Signals(QObject):
    result   = Signal(object)
    error    = Signal(str)
    progress = Signal(int)

class Worker(QRunnable):
    def __init__(self, fn: Callable, *args, **kwargs):
        super().__init__()
        self.fn, self.args, self.kwargs = fn, args, kwargs
        self.signals = _Signals()
        self.setAutoDelete(True)

    def run(self):
        try:
            self.signals.result.emit(self.fn(*self.args, **self.kwargs))
        except Exception as e:
            self.signals.error.emit(str(e))

# ✅ Отдельный пул (не globalInstance): не конфликтует с внутренними задачами Qt
_pool = QThreadPool()
_pool.setMaxThreadCount(4)

def run_async(fn, *args, on_result=None, on_error=None, on_progress=None, **kwargs) -> Worker:
    w = Worker(fn, *args, **kwargs)
    if on_result:   w.signals.result.connect(on_result)
    if on_error:    w.signals.error.connect(on_error)
    if on_progress: w.signals.progress.connect(on_progress)
    # ⚠️ on_progress: fn должна принимать progress_cb и вызывать его явно:
    #   def my_task(progress_cb=None): ... if progress_cb: progress_cb(50)
    #   run_async(my_task, progress_cb=w.signals.progress.emit, on_progress=update_ui)
    _pool.start(w); return w
```

ПРАВИЛО: НИКОГДА не обращаться к GUI-виджетам из worker-потоков.
Передача данных: только через Qt-сигналы (thread-safe).

---

## 5. SVG-ИКОНКИ — ПОЛНЫЙ КАТАЛОГ (55 штук)

```python
# ui/styles/icons.py
# Категории: навигация (10), действия (20), контент (25) = 55 иконок

_SVG_ICONS = {
    # Навигация
    "home":           '...',
    "cases":          '...',
    "results":        '...',
    "analytics":      '...',
    "groups":         '...',
    "settings":       '...',
    "profile":        '...',
    "users":          '...',
    "logs":           '...',
    "system":         '...',

    # Действия
    "add":            '...',
    "edit":           '...',
    "delete":         '...',
    "save":           '...',
    "publish":        '...',
    "duplicate":      '...',
    "export":         '...',
    "search":         '...',
    "filter":         '...',
    "close":          '...',
    "back":           '...',
    "forward":        '...',
    "refresh":        '...',
    "sort":           '...',
    "drag":           '...',
    "hint":           '...',
    "check":          '...',
    "check_circle":   '...',
    "error_circle":   '...',
    "warning":        '...',

    # Контент
    "book":           '...',
    "virus":          '...',
    "bacteria":       '...',
    "shield_medical": '...',
    "module":         '...',
    "task":           '...',
    "branch":         '...',
    "image":          '...',
    "table":          '...',
    "timeline":       '...',
    "formula":        '...',
    "document":       '...',
    "play":           '...',
    "pause":          '...',
    "trophy":         '...',
    "star":           '...',
    "clock":          '...',
    "password":       '...',
    "logout":         '...',
    "backup":         '...',
    "theme":          '...',
    "question":       '...',
    "drag_handle":    '...',
    "chevron_right":  '...',
    "chevron_down":   '...',
}
# Каждая иконка — inline SVG строка с fill="currentColor"
# get_icon(name, color, size) → QIcon через QSvgRenderer + QPainter

def get_icon(name: str, color: str = "#1A1A1A", size: int = 20) -> "QIcon":
    svg = _SVG_ICONS.get(name, _SVG_ICONS["question"])
    svg = svg.replace("currentColor", color)
    # ... рендер через QSvgRenderer → QPixmap → QIcon
```

---

## 6. ДИЗАЙН-ТОКЕНЫ (theme.py полная версия)

```python
# ui/styles/theme.py

COLORS = {
    # Акцент
    "accent":           "#0078D4",
    "accent_hover":     "#006CBD",
    "accent_pressed":   "#005BA5",
    "accent_light":     "#4DA3E8",
    "accent_dark":      "#005A9E",

    # Семантические
    "success":      "#107C10",  "success_bg":  "#DFF6DD",
    "warning":      "#9D5D00",  "warning_bg":  "#FFF4CE",
    "error":        "#C42B1C",  "error_bg":    "#FDE7E9",
    "info":         "#0078D4",  "info_bg":     "#EFF6FC",

    # Фоны
    "bg_base":      "#F3F3F3",  # основной фон
    "bg_elevated":  "#FFFFFF",  # карточки
    "bg_layer":     "#FAFAFA",  # вложенные элементы
    "sidebar_bg":   "#EEEEEE",

    # Текст
    "text_primary":   "#1A1A1A",
    "text_secondary": "#6B6B6B",
    "text_disabled":  "#ABABAB",
    "text_on_accent": "#FFFFFF",
    "text_link":      "#0078D4",

    # Состояния
    "state_hover":    "rgba(0,0,0,0.04)",
    "state_pressed":  "rgba(0,0,0,0.08)",
    "state_selected": "rgba(0,120,212,0.10)",

    # Обводки
    "stroke_card":    "rgba(0,0,0,0.08)",
    "stroke_control": "rgba(0,0,0,0.14)",
    "stroke_divider": "rgba(0,0,0,0.05)",
}

RADIUS  = {"control": 4, "card": 8, "overlay": 8, "large": 12, "xlarge": 16}
SPACING = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24, "xxl": 32}
TYPO    = {
    "font": "Segoe UI Variable, Segoe UI, DejaVu Sans, Arial",  # загружаем из assets/fonts/ при старте
    "display": 40, "title_large": 28, "title": 20,
    "subtitle": 16, "body_large": 14, "body": 13, "caption": 11
}
ANIM    = {
    "instant": 80,   # hover press, immediate feedback
    "fast":    150,   # hover enter/leave, badge
    "normal":  220,   # page transitions, sidebar item
    "medium":  300,   # toast, dialogs, progress
    "slow":    500,   # progress ring fill, score counter
}
# ✅ убрано дублирование "normal"≈"medium"; добавлен "instant" для hover
```

---

## 7. СИСТЕМА АНИМАЦИЙ — ПОЛНАЯ СПЕЦИФИКАЦИЯ

```python
# ui/styles/animations.py

# ── 1. fade_in(widget, duration=200)
#    opacity: 0.0 → 1.0 | OutCubic | QGraphicsOpacityEffect

# ── 2. fade_out(widget, duration=100, on_done=None)
#    opacity: 1.0 → 0.0 | InCubic → on_done callback

# ── 3. slide_up(widget, offset=20, duration=300)
#    pos.y: +offset → 0  ПАРАЛЛЕЛЬНО  opacity: 0 → 1
#    easing: OutExpo (резкий старт, плавное замедление)

# ── 4. slide_from_right(widget, duration=250)
#    pos.x: +30 → 0  ПАРАЛЛЕЛЬНО  opacity: 0 → 1
#    easing: OutCubic — переход между страницами

# ── 5. sidebar_expand(sidebar, from_w=60, to_w=240, duration=200)
#    min/maxWidth анимируются одновременно | OutCubic
#    При collapse: текст labels fade_out(100ms) одновременно

# ── 6. shake(widget)
#    pos.x последовательно: -4 → +4 → -4 → +4 → -2 → +2 → 0
#    50ms на каждый шаг | OutSine — неверный ответ

# ── 7. stagger_cards(cards, delay_ms=50)
#    Для каждой карточки: QTimer.singleShot(i*delay, fade_in)
#    Эффект каскадного появления

# ── 8. score_pop(label)
#    ⚠️ QPropertyAnimation НЕ может анимировать font size напрямую
#    ✅ Реализация: QSequentialAnimationGroup из двух QTimer + label.setFont()
#    step1 (40ms): setFont(size+4) → step2 (80ms OutBack): setFont(size)
#    Эффект: "подпрыгивание" числа баллов на экране результата

# ── 9. progress_ring_fill(ring_widget, from_val=0, to_val=X, duration=1500)
#    QPropertyAnimation на custom property "value"
#    OutCubic — плавное заполнение кольца на экране результата

# ── 10. feedback_correct(widget)
#     bg: transparent → success_bg | fade_in 100ms
#     + check_circle icon scale: 0 → 1 | 150ms OutBack

# ── 11. feedback_wrong(widget)
#     bg: transparent → error_bg | fade_in 100ms
#     + shake(widget) 350ms

# ── 12. toast_show/hide(toast)
#     Вход:  slide_up(40px) + fade_in | 300ms OutExpo
#     Выход: fade_out | 200ms InCubic → deleteLater
#     Auto: QTimer 4000ms (info/success), 6000ms (error)

# ── 13. loading_skeleton shimmer
#     Используется: LoadingOverlay, перекрывает контент во время run_async
#     QWidget с кастомным paintEvent:
#       фон: сплошной QColor("#E8E8E8")
#       бегущая полоса: QLinearGradient(transparent→#FFFFFF@50%→transparent, ширина=40% виджета)
#     Анимация: QPropertyAnimation(self, b"shimmer_pos"), 0.0→1.0
#       duration=1200ms | Linear | setLoopCount(-1) — бесконечный цикл
#     shimmer_pos — Qt-свойство (Property float): сдвигает x-стартовую позицию градиента
#       start_x = int(widget.width() * (shimmer_pos - 0.4))
#     Остановка: anim.stop() + overlay.hide() + overlay.deleteLater()

# ── 14. slide_in_right(panel, width=300, duration=220)
#     pos.x: parent.width → parent.width-width | OutCubic
#     Используется: A-2 DockPanel при клике на строку пользователя
#     QPainter LinearGradient: серый фон + светлая полоса
#     QPropertyAnimation: смещение градиента 0 → 100% | 1200ms Linear | loop
```

---

## 8. ОПИСАНИЕ ВСЕХ 21 ЭКРАНА

### LOGIN WINDOW

```
Размер: 480×600px, FramelessWindowHint, centered
Drag: mousePressEvent/mouseMoveEvent на кастомном titlebar

[ SVG логотип 64px ] [ EduCase ] [ ВМедА им. С.М. Кирова ]
[ QLineEdit: Логин    — иконка profile слева ]
[ QLineEdit: Пароль   — иконка password + кнопка 👁 ]
[ QPushButton ВОЙТИ   — полная ширина, h=44px, accent ]
[ QLabel: ошибка      — fade_in красный, скрыт по умолчанию ]
[ QLabel: "Забыли пароль? Обратитесь к администратору" — caption, secondary, centered ]
[ version label       — v1.0.0, caption, secondary ]

Блокировка: кнопка меняет текст "Подождите 4:59..."
            + QTimer обратного отсчёта
Успех: fade_out(LoginWindow) → fade_in(MainWindow) + bus.user_logged_in
```

### MAIN WINDOW

```
FramelessWindowHint + кастомный TitleBar (drag + min/close)
QHBoxLayout: Sidebar (setFixedWidth) | QStackedWidget (content)
# ✅ НЕ QSplitter — ширина Sidebar задаётся через setFixedWidth / анимация QPropertyAnimation

Sidebar (QWidget, фиксированная ширина 60/240px):
  - Avatar (32px collapse / 40px expand)
  - FullName (только expand, body_large)
  - Разделитель
  - NavItems по роли:
    student:  Home, Cases, Results, Profile
    teacher:  Home, Cases, Analytics, Groups, Profile
    admin:    Home, Users, System, Logs, Profile
  - Внизу: кнопка Logout + toggle expand/collapse
  - Active item: левая полоска 3px accent + selected bg

Content: QStackedWidget, переключается через bus.navigate_to
```

### S-1: StudentDashboard

```
TopBar: "Добро пожаловать, Иванов И.И." + текущая дата

StatCard × 3: [Доступно кейсов: 12] [Выполнено: 8] [Средний балл: 78%]

Section "Продолжить" (если есть активная попытка):
  CaseCard + прогресс + [Продолжить] кнопка

Section "Рекомендовано" (горизонтальный scroll):
  3-4 CaseCard (неначатые из группы)

Section "Последние результаты":
  StyledTableView 5 строк: Кейс | Дисциплина | Балл | Дата

EmptyState (нет назначенных кейсов): иконка + "Кейсы ещё не назначены"
```

### S-2: MyCases

```
TopBar: "Мои кейсы" + SearchBar + DropDown(дисциплина)
# ✅ DropDown(статус) убран — дублировал Tabs

Tabs: [Все] [Новые] [В процессе] [Завершённые]

QGridLayout 3 колонки → CaseCard:
  - Cover (градиент-заглушка с иконкой если нет фото)
  - Badge: Новый/В процессе/Завершён
  - Title (2 строки max, ellipsis)
  - Дисциплина > Тема (secondary)
  - AnimatedProgressBar (0-100%)
  - Балл: "87/100 ⭐" (при завершении)
  - Button hover: [Начать]/[Продолжить]/[Повторить]

Hover effect: translateY(-2px, 150ms OutBack) + усиление тени
Stagger: карточки появляются каскадом (delay=50ms)
EmptyState если нет кейсов
```

### S-3: CasePlayer

```
Header (фиксированный):
  [← Выйти] | Название кейса | [⏸ Пауза] | [⏱ Таймер]  ← только если time_limit_min IS NOT NULL

ProgressSection:
  "Модуль X из Y: Название"
  AnimatedProgressBar + "Задание Z из W" + ScoreBadge "18/30 баллов"

ContentArea (scrollable):
  TaskTitle (title-style, 20pt)
  TaskBody (QTextBrowser, HTML)
  TaskWidget (конкретный тип) — заполняет всю доступную высоту

BottomBar (фиксированный):
  [💡 Подсказка (fade-in tooltip)] | [← Предыдущее] | [Проверить →]
  # [← Предыдущее]: переход к предыд. заданию модуля, скрыт на первом; ≠ [← Выйти] из Header

FeedbackPanel (slide_up поверх BottomBar, h=100px):
  ✅ зелёный / ❌ красный + shake / ⚠ жёлтый
  + объяснение текстом
  + [Далее →]

Пауза: QGraphicsBlurEffect(2px) + центральный overlay-диалог
```

### S-4: CaseResult

```
ProgressRing (180px) — анимация заполнения 1.5s, цвет по % (красный/жёлтый/зелёный)
"X / Y баллов" под кольцом (score_pop анимация)
"Оценка: 4" (badge)

ModuleBreakdown (Accordion):
  ▼ Модуль 1: Первичные данные   ████████████░░  8/10 (80%)
  ▼ Модуль 2: Обследование очага ██████████████ 14/15 (93%)

Ошибки:
  Список TaskCard с красной рамкой:
  Задание 3: "Расчёт показателей"
    Ваш ответ: 12.4  |  Правильно: 14.2  |  +0 баллов

Кнопки: [Повторить] ← disabled/скрыт если attempt_num >= max_attempts
         [К кейсам] [📄 Скачать отчёт]
```

### S-5: MyResults

```
TopBar + DateRangePicker + DropDown(дисциплина)

График (matplotlib FigureCanvas 380px):
  Scatter+line: дата → % балла
  Пунктирная линия "порог 60%"

StyledTableView:
  Кейс | Дисциплина | Дата | Время | % | Оценка | [Подробнее]
  При клике "Подробнее" → bus.navigate_to('case_result', {'attempt_id': id, 'readonly': True})
```

### S-6: Profile

```
Avatar (96px, кликабельный ImagePicker) + ФИО + Роль + Группа

Форма: ФИО QLineEdit, Логин (read-only)
Смена пароля (Accordion):
  Текущий пароль | Новый | Подтверждение
  Индикатор сложности: weak(red) / fair(yellow) / strong(green)
  weak=<8 симв; fair=≥8 букв+цифр; strong=≥10+заглавные+спецсимволы
[Сохранить изменения] + Toast при успехе
```

### T-1: TeacherDashboard

```
StatCard × 4: [Мои кейсы: 8] [Опубликовано: 5] [Студентов: 34] [Попыток сегодня: 12]
Активные группы: GroupCard карточки
Лента активности: "Иванов завершил 'Гепатит А' — 87%" | 10 мин назад

EmptyState (нет кейсов/групп): иконка + "Создайте первый кейс" + [+ Создать кейс]
```

### T-2: MyCases

```
TopBar + [+ Создать кейс] (акцентная кнопка, правый верхний угол)
Фильтры: Tabs [Все][Черновики][Опубликованные][Архив]

List view (не grid):
  [обложка 64×64] | Название + статус Badge | Дисциплина > Тема
                   | "4 модуля · 24 задания · 3 группы"
                   | [Редактировать] [Аналитика] [⋮]
  Меню ⋮: Дублировать | Архивировать | Удалить | Экспорт JSON
```

### T-3: CaseEditor

```
SplitView: TreePanel(300px) | DetailPanel(расширяемый)

TreePanel (QTreeWidget с drag-drop для реорядка):
  📁 Название кейса
    ├─ ⬜ ≡ Модуль 1  [⋮ добавить задание, удалить]  ← ≡ = drag handle
    │    ├─ 📄 ≡ Задание 1   ← drag handle (порядок внутри модуля)
    │    └─ 📄 ≡ Задание 2
    └─ [+ Добавить модуль]

DetailPanel меняется по выбору:
  Кейс → мета-данные (title, desc, cover ImagePicker, topic, settings)
  Модуль → название, тип linear/branching
  Задание → открывается TaskConstructorDialog

TopBar: [💾 Сохранить] [👁 Предпросмотр] [🚀 Опубликовать]
Закрытие с несохранёнными изменениями → ConfirmDialog: "Сохранить перед выходом?" [Сохранить] [Не сохранять] [Отмена]
```

### T-4: TaskConstructor (диалог 900×700px)

```
3-панельный layout:

TypeSelector (180px, левая):
  12 карточек типов (иконка + название)
  Активный тип: accent border + bg_selected

TaskEditor (центр, ~55%):
  RichTextEditor для условия
  Специфичные поля типа
  Настройки: max_score, penalty, partial_credit, hint

PreviewPanel (правая, ~30%):
  Заголовок "Предпросмотр"
  Live TaskWidget — обновляется по сигналу:
  QLineEdit.textChanged / QCheckBox.toggled → QTimer debounce 300ms → rebuild widget
  (деактивирован — только просмотр)

Кнопки: [Отмена] ← несохранённые изменения → ConfirmDialog / [Сохранить задание]
```

### T-5: ScenarioBuilder (диалог, fullscreen)

```
Toolbar: [+ Узел ▾] [Auto-layout] [Fit] [↩ Undo Ctrl+Z] [↪ Redo Ctrl+Y] [Валидировать] [Сохранить]
Undo/Redo: QUndoStack — каждое действие (добавить узел/ребро, переместить, удалить) = QUndoCommand

GraphView (QGraphicsView):
  Zoom: Ctrl+Scroll, fit: F
  Pan: Space+drag

  Узлы (QGraphicsItem):
    START:   синий     rounded rect 140×50
    ВОПРОС:  серый     140×50
    ИНФОРМ.: голубой   140×50
    УСПЕХ:   зелёный   140×50
    ОШИБКА:  красный   140×50
    КОНЕЦ:   тёмный    140×50

  Создание ребра: drag от порта (●) на краю узла к другому узлу
  Стрелка: QGraphicsPathItem + arrowhead + QGraphicsTextItem(label)

  Двойной клик на узле → диалог: title, content (RichTextEditor)
  Клик на ребро → боковая панель: label, score_delta, is_correct

Валидация:
  ✅ есть ровно один START
  ✅ есть хотя бы один END
  ✅ нет изолированных узлов
  ✅ все узлы достижимы из START
```

### T-6: Analytics

```
TopBar + DropDown(группа) + DropDown(кейс) + DateRangePicker

StatCard × 4: [Ср. балл: 74%] [Завершили: 28/34] [Ср. время: 18 мин] [Лучший: 98%]

Тепловая карта (matplotlib 500px):
  X: задания (1..24)
  Y: студенты (Студент 1..28)
  Цвет: красный(0%) → зелёный(100%)

Гистограмма оценок (matplotlib 300px):
  Bins 0-10..90-100, пунктир "порог зачёта"

Таблица проблемных заданий:
  Задание | Тип | Ср. балл | Кол-во попыток
  Сортировка по ср. баллу по возрастанию

[📥 Экспорт PDF] [📊 Экспорт Excel] — run_async
```

### T-7: Groups

```
[+ Создать группу] кнопка

Grid GroupCard:
  Название | N студентов | N кейсов | Преподаватель
  [Открыть] [Редактировать] [Удалить]

EmptyState (нет групп): иконка + "Создайте первую группу" + [+ Создать группу]
```

### T-8: GroupDetail

```
TopBar: "Группа №2" + [← Назад] + [+ Добавить студента] + [Привязать кейс]

Tabs: [Студенты] [Кейсы] [Результаты]

Студенты: StyledTableView
  ФИО | Логин | Последний вход | Ср. балл | [Удалить из группы]

Диалог добавления студента:
  SearchBar live-search → список → клик = добавить

Кейсы: список кейсов с возможностью отвязать

Результаты: mini-аналитика группы по кейсам
```

### A-1: AdminDashboard

```
StatCard × 4: [Пользователей: 47] [Студентов: 40] [Преп.: 5] [Кейсов: 23]

Системная информация QFrame:
  Размер БД: 14.2 MB | Последний бэкап: 2 ч назад | v1.0.0

Bar chart (matplotlib): активность последних 7 дней
  Синие: попытки, Зелёные: завершённые кейсы
```

### A-2: Users

```
TopBar + [+ Создать] + SearchBar + DropDown(роль) + DropDown(статус)

StyledTableView (сортируемая):
  ФИО | Логин | Роль badge | Группа | Статус | Последний вход | Действия

Клик на строку → боковая DockPanel slide_in_right (300px):
  Аватар + детали + кнопки [Редактировать] [Заблокировать]

Bulk-select: checkbox + [Блокировать выбранных] [Удалить выбранных]
```

### A-3: UserEditor (диалог)

```
Stepper 2 шага:
[1. Основное] ──── [2. Права]

Шаг 1:
  ImagePicker (аватар, 96px, круглый preview)
  ФИО, Логин, Роль (Select), Группа (Select)
  Пароль + подтверждение (при создании)
  [👁 Показать] + [🔀 Сгенерировать] — генерирует 12-символьный пароль, копирует в буфер
  Toggle: Активен/Заблокирован

Шаг 2:
  Если роль не стандартная — матрица чекбоксов прав
  Иначе: "Права назначены автоматически по роли"

[Назад] [Создать пользователя / Сохранить]
```

### A-4: System

```
Tabs: [Общее] [База данных] [Резервные копии] [Дизайн]

Общее:
  Версия, путь к файлу БД, язык интерфейса

БД:
  Размер файла, кол-во записей по таблицам
  [VACUUM] (с LoadingOverlay) [Проверить целостность]

Бэкапы:
  Список: файл | дата | размер | [Восстановить] [Удалить]
  [Создать бэкап] — run_async + Toast при завершении
  Toggle AutoBackup + выбор дней хранения

Дизайн:
  ColorPicker (акцент)
  QSlider анимаций (0.5x — 2.0x)
  Toggle Светлая/Тёмная тема
```

### A-5: Logs

```
TopBar + DateRange + DropDown(уровень) + DropDown(пользователь) + SearchBar

StyledTableView:
  Время | Уровень (Badge: INFO/WARNING/ERROR) | Пользователь | Действие | Детали...
  Клик → диалог: JSON деталей с подсветкой

[Экспорт CSV] [Очистить >90 дней] (с ConfirmDialog)
```

---

## 8.5 СЕРВИСЫ — BackupService

```python
# services/backup_service.py
import shutil, sqlite3
from datetime import datetime
from pathlib import Path
from sqlalchemy import text
from config import BACKUP_DIR, DB_PATH, CONFIG
from core.database import engine
from core.event_bus import bus
from core.exceptions import AppError

class BackupService:
    def create(self) -> Path:
        """Безопасный бэкап SQLite через sqlite3.Connection.backup() (WAL-safe)."""
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = BACKUP_DIR / f"backup_{ts}.db"
        # ✅ sqlite3.Connection.backup() — единственный надёжный способ
        #    при WAL-mode (shutil.copy2 может скопировать в середине транзакции)
        src_conn = sqlite3.connect(str(DB_PATH))
        dst_conn = sqlite3.connect(str(dest))
        with dst_conn:
            src_conn.backup(dst_conn, pages=256)  # 256 страниц за раз (~1MB)
        src_conn.close(); dst_conn.close()
        self._prune(keep=CONFIG.backup_count)
        # ✅ логируем в system_logs (отображается в A-5)
        with engine.begin() as conn:
            conn.execute(text(
                "INSERT INTO system_logs(level,action,details) VALUES('INFO','backup_created',:d)"
            ), {"d": str(dest.name)})
        return dest

    def restore(self, backup_path: Path) -> None:
        """Восстановление: заменяем БД, перезапускаем engine."""
        engine.dispose()          # закрыть все соединения SQLAlchemy
        for suffix in ["-wal", "-shm"]:  # ✅ удалить WAL-файлы
            DB_PATH.with_suffix(DB_PATH.suffix + suffix).unlink(missing_ok=True)
        # ✅ integrity_check перед заменой
        chk = sqlite3.connect(str(backup_path))
        ok  = chk.execute("PRAGMA integrity_check").fetchone()[0]
        chk.close()
        if ok != "ok": raise AppError(f"Бэкап повреждён: {ok}")
        shutil.copy2(backup_path, DB_PATH)
        # после восстановления — нужен рестарт приложения
        bus.show_toast.emit("БД восстановлена. Перезапустите приложение.", "success")

    def list_backups(self) -> list[dict]:
        return sorted(
            [{"path": p, "name": p.name,
              "size_mb": round(p.stat().st_size/1024/1024, 2),
              "date": datetime.fromtimestamp(p.stat().st_mtime)}
             for p in BACKUP_DIR.glob("backup_*.db")],
            key=lambda x: x["date"], reverse=True
        )

    def _prune(self, keep: int) -> None:
        """Удалить старые бэкапы, оставить только keep штук."""
        all_backups = self.list_backups()
        for b in all_backups[keep:]:
            b["path"].unlink(missing_ok=True)
```

---

## 8.6 СЕРВИСЫ — ExportService

```python
# services/export_service.py
# ExportService(analytics_service, attempt_repo)

# PDF-отчёт по попытке студента (reportlab):
#   Шапка: логотип ВМедА, ФИО, дата, кейс
#   Сводка: балл / макс, % правильных, оценка, время
#   Таблица: №  Задание  Тип  Балл  Макс  Верно
#   Ошибки: задание + мой ответ + правильный ответ
#   Подвал: дата генерации, подпись

# Excel-отчёт по группе (openpyxl):
#   Лист 1 "Сводка": студент × кейс → % балл
#   Лист 2 "Детали": каждый ответ каждого студента
#   Лист 3 "Статистика": ср. балл, медиана, σ по каждому заданию
#   Условное форматирование: зелёный ≥75%, жёлтый ≥60%, красный <60%
#   Заморозка первой строки + первого столбца (freeze_panes)

# Оба генерируются в MEDIA_DIR/exports/ → открываются через:
# QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))  # ✅ не голая строка
```

---

## 9. GRADER SERVICE — ЛОГИКА ОЦЕНИВАНИЯ ВСЕХ ТИПОВ

```python
# services/grader_service.py
from dataclasses import dataclass

@dataclass
class GradeResult:
    score:      float  # полученных баллов
    max_score:  float  # максимум за задание
    is_correct: bool   # True если score == max_score (полный балл); False при partial или неверном
    details:    dict   # {"matched":["туляремия"],"wrong_options":[3]}

# grade(task: Task, answer_data: dict) -> GradeResult
# Диспетчер по task.task_type, вызывает нужный приватный метод

# single_choice:    выбранный option_id == correct option → max_score
# multi_choice:     partial_credit если включён:
#                   if total_correct == 0: return GradeResult(0, max_score, False, {"error":"no_correct_options"})
#                   score = max * (correct_selected - wrong_selected) / total_correct
#                   ⚠️ max(score, 0) — нельзя уйти в минус за один вопрос
#                   wrong_selected = выбранные студентом неверные варианты
# text_input:       for kw in task.keywords:
#                       words = [kw.keyword] + json.loads(kw.synonyms)
#                       if any(w.lower() in answer.lower() for w in words): score += kw.score_value
#                   ⚠️ синонимы используются при проверке
#                   ⚠️ сумма score_value всех keywords должна = task.max_score
#                   Валидация в TaskService при сохранении задания
# form_fill:        score = sum(f.score_value for f in correctly_filled_fields)
# ordering:         if total_items == 0: return GradeResult(0, max_score, False, {"error":"no_items"})
#                   полный = max_score; частичный = max * (верных_позиций / total_items)
# matching:         if total_pairs == 0: return GradeResult(0, max_score, False, {"error":"no_pairs"})
#                   score = max * (верных_пар / total_pairs)
# calculation:      try: val = float(answer_data["value"])
#                   except (ValueError, KeyError): return GradeResult(0, max_score, False, {"error":"not_a_number"})
#                   score = max_score if abs(val - correct_value) <= tolerance else 0
#                   ⚠️ tolerance — абсолютная, НЕ relative (relative ломается при correct=0)
#                   В редакторе: преподаватель задаёт tolerance напрямую (например, 0.5)
# image_annotation: кликнутая (x,y) попадает в is_correct зону
#   Координаты нормализованы [0.0, 1.0] относительно размера изображения
#   Hit-test: zone.x <= click_x <= zone.x+zone.width AND zone.y <= click_y <= zone.y+zone.height
#   Виджет переводит пиксельный клик в [0,1]: norm_x = px / img_width
# timeline:         как ordering — позиции событий на оси
# table_input:      if editable_cells == 0: return GradeResult(0, max_score, False, {"error":"no_editable_cells"})
#                   score = max * (верных_ячеек / editable_cells)
# document_editor:  keyword-детекция в тексте документа (как text_input)
# branching:        score_delta из ScenarioEdge (может быть отрицательным)

# ── ЛОГИКА penalty_score (применяется в grade() ПОСЛЕ вычисления score):
# if not result.is_correct and task.penalty_score > 0:
#     result.score = max(0.0, result.score - task.penalty_score)
# ⚠️ penalty применяется только при полностью неверном ответе (is_correct=False)
# ⚠️ при partial_credit penalty НЕ применяется (частичный балл сохраняется)
# ⚠️ итоговый score никогда не уходит ниже 0.0 за одно задание
```

---

## 10. ПОЛНЫЙ TODO ЛИСТ v2

### ЭТАП 0 — Scaffolding (~3 дня)

- [x] main.py (точка входа: QApp + QFontDatabase.addApplicationFont + \_init_dirs + SplashScreen + run_migrations + build_container + LoginWindow, см. §15.4)
- [x] app.py (модульный синглтон: current_user, config, get_session)
- [x] pyproject.toml (black, ruff, mypy конфиги)
- [x] requirements.txt и requirements-dev.txt с точными версиями
- [x] Вся структура папок (mkdir -p)
- [x] config.py: AppConfig, DATA_DIR, MEDIA_LIMITS
- [x] core/logger.py: loguru, ротация, sink→system_logs
- [x] core/exceptions.py: все типы ошибок
- [x] core/event_bus.py: EventBus singleton
- [x] core/di_container.py: Container (сборка зависимостей)
- [x] core/thread_pool.py: Worker, run_async
- [x] core/validators.py: validate_username, validate_password, validate_image
- [x] ui/styles/theme.py: все токены
- [x] ui/styles/icons.py: 55 иконок inline
- [x] ui/styles/stylesheet.py: глобальный QSS
- [x] ui/styles/animations.py: все 14 анимаций (см. §7)
- [x] pre-commit: black + ruff хуки
- [x] ui/windows/splash_window.py — SplashScreen (paintEvent + анимации, §15.3 + §16)
- [x] assets/icon_master.svg — мастер SVG иконки (256×256 viewBox, §14)
- [x] tools/make_ico.py — генерация assets/icon.ico (cairosvg + Pillow, §14.2 + §16.1)
- [x] Запустить make_ico.py → assets/icon.ico
- [x] QApplication.setWindowIcon(QIcon("assets/icon.ico")) в main.py

### ЭТАП 1 — БД + Auth (~4 дня)

- [x] models/base.py, models/user.py
- [x] core/database.py + PRAGMA
- [x] core/db_maintenance.py
- [x] Alembic init + migration 001
- [x] repositories/base.py (generic)
- [x] repositories/user_repo.py
- [x] repositories/group_repo.py
- [x] services/auth_service.py (login, logout, lockout, permission check)
- [x] services/user_service.py (create, update, change_password)
- [x] Seed: роли + 3 тестовых пользователя + 3 дисциплины
- [x] ui/components/toast.py (ToastManager, 4 типа, анимации)
- [x] ui/windows/login_window.py (drag, блокировка, анимации)
- [x] ui/windows/main_window.py (titlebar, QStackedWidget)
- [x] ui/components/sidebar.py (анимации expand/collapse, role-aware nav)
- [x] ui/components/topbar.py
- [x] tests/conftest.py (fixtures: in_memory_db с StaticPool, session, container, seed_users)
- [x] tests/unit/test_auth.py

### ЭТАП 2 — Модели контента (~4 дня) ✅

- [x] models/content.py (Discipline, Topic, Case, CaseGroup, Module)
- [x] models/task.py (Task + 8 подтаблиц)
- [x] models/scenario.py
- [x] models/media.py, models/system.py, models/attempt.py
- [x] migration 002_content_schema (disciplines/topics/cases/modules/tasks/scenarios/attempts/media)
- [x] migration 003_system_settings (system_settings, system_logs)
- [x] repositories/case_repo.py, module_repo.py, task_repo.py, scenario_repo.py
- [x] repositories/media_repo.py, attempt_repo.py, analytics_repo.py
- [x] services/case_service.py, module_service.py, task_service.py
- [x] services/media_service.py (upload/validate/resize)
- [x] services/backup_service.py
- [x] tests/unit/test_services.py

### ЭТАП 3 — UI-компоненты (~5 дней) ✅

- [x] card.py + hover-анимация
- [x] case_card.py (cover, badge, progress, button)
- [x] stat_card.py
- [x] badge.py (4 цвета)
- [x] avatar.py (инициалы fallback)
- [x] progress_ring.py (QPainter + QPropertyAnimation)
- [x] progress_bar.py (animated fill)
- [x] dialog.py (BaseDialog, ConfirmDialog, InputDialog)
- [x] table_view.py (sorting, hover rows, striped)
- [x] search_bar.py (expand animation)
- [x] empty_state.py
- [x] loading_overlay.py (spinner + blur)
- [x] rich_text_editor.py # Основан на QTextEdit; toolbar: жирный/курсив/список/заголовок/вставка изображения; экспортирует HTML (сохраняется в tasks.body и cases.description)
- [x] image_picker.py (drag&drop + dialog + preview)
- [x] accordion.py, stepper.py, color_picker.py, score_badge.py

### ЭТАП 4 — Конструктор заданий (~12 дней)

- [ ] task_constructor/base_editor.py (AbstractTaskEditor)
- [ ] constructor_dialog.py (3-panel layout)
- [ ] type_selector.py (12 карточек типов)
- [ ] preview_panel.py (live TaskWidget)
- [ ] Editor: SingleChoice
- [ ] Editor: MultiChoice
- [ ] Editor: TextInput (таблица ключевых слов + синонимы)
- [ ] Editor: FormFill (конструктор полей)
- [ ] Editor: Ordering (drag&drop реорганизация)
- [ ] Editor: Matching (два столбца с соединениями)
- [ ] Editor: Calculation (значение + допуск + единицы)
- [ ] Editor: ImageAnnotation (upload + рисование зон)
- [ ] Editor: Timeline (ось + события)
- [ ] Editor: TableInput (настройка строк/столбцов/значений)
- [ ] Editor: DocumentEditor (загрузка .docx + маркировка полей)
- [ ] Editor: Branching (открывает ScenarioBuilder)
- [ ] scenario_builder/graph_scene.py
- [ ] scenario_builder/graph_view.py (zoom, pan, fit)
- [ ] scenario_builder/node_item.py (drag, contextmenu, double-click edit)
- [ ] scenario_builder/edge_item.py (кривая Безье + стрелка + label)
- [ ] Валидация сценария
- [ ] tests/unit/test_task_service.py

### ЭТАП 5 — Плеер кейсов (~10 дней)

- [ ] services/grader_service.py (все 12 типов)
- [ ] services/scenario_service.py (traverse)
- [ ] services/attempt_service.py (start/resume/save_answer/finish/abandon/pause/get_progress)
- [ ] task_widgets/base_task_widget.py
- [ ] TaskWidget: SingleChoice
- [ ] TaskWidget: MultiChoice
- [ ] TaskWidget: TextInput
- [ ] TaskWidget: FormFill
- [ ] TaskWidget: Ordering (QListWidget drag&drop)
- [ ] TaskWidget: Matching (QPainter линии)
- [ ] TaskWidget: Calculation
- [ ] TaskWidget: ImageAnnotation (QGraphicsView + клик + zoom)
- [ ] TaskWidget: Branching (крупные кнопки)
- [ ] TaskWidget: DocumentEditor
- [ ] TaskWidget: Timeline
- [ ] TaskWidget: TableInput
- [ ] screens/student/case_player.py (header+progress+content+bottombar)
- [ ] FeedbackPanel (slide_up + 3 состояния)
- [ ] Shake-анимация при неверном ответе
- [ ] QTimer авто-сохранение каждые 30 сек
- [ ] Механизм паузы: attempt_service.pause() + QGraphicsBlurEffect(2px) + overlay
- [ ] Resume при повторном входе
- [ ] Таймер кейса (time_limit_min)
- [ ] screens/student/case_result.py (ProgressRing анимация 1.5s)
- [ ] tests/unit/test_grader_all_types.py
- [ ] tests/unit/test_scenario_traversal.py

### ЭТАП 6 — Экраны студента (~4 дня)

- [ ] screens/student/dashboard.py + presenter
- [ ] screens/student/my_cases.py (grid + stagger) + presenter
- [ ] screens/student/my_results.py (matplotlib) + presenter
- [ ] screens/student/profile.py (avatar + форма + смена пароля) + presenter
- [ ] slide_from_right при смене страниц

### ЭТАП 7 — Экраны преподавателя (~6 дней)

- [ ] screens/teacher/dashboard.py + presenter
- [ ] screens/teacher/my_cases.py + presenter
- [ ] screens/teacher/case_editor.py (tree+detail) + presenter
- [ ] screens/teacher/analytics.py (heatmap + histogram) + presenter
- [ ] screens/teacher/groups.py + group_detail.py + presenter
- [ ] services/analytics_service.py
- [ ] services/export_service.py (PDF + Excel)
- [ ] tests/unit/test_analytics.py, test_export.py

### ЭТАП 8 — Экраны администратора (~4 дня)

- [ ] screens/admin/dashboard.py + presenter
- [ ] screens/admin/users.py (table + dock panel) + presenter
- [ ] screens/admin/user_editor.py (stepper) + presenter
- [ ] screens/admin/system.py (4 вкладки) + presenter
- [ ] screens/admin/logs.py (table + JSON диалог) + presenter

### ЭТАП 9 — Полировка (~5 дней)

- [ ] Все EmptyState на всех экранах
- [ ] LoadingOverlay на все run_async операции
- [ ] ConfirmDialog на все деструктивные операции
- [ ] Keyboard navigation (Tab/Enter/Esc/Ctrl+S)
- [ ] setTabOrder() явно задан для всех форм (логин, редактор задания, профиль, UserEditor)
- [ ] Tooltips на все иконки без текста
- [ ] DPI-адаптация (devicePixelRatio для иконок)
- [ ] Resize окна → адаптация grid (3→2→1 колонки)
- [ ] Тёмная тема (переключение ColorTokens + QSS regeneration) ← V3 фича, заложить архитектуру в Этапе 9
- [ ] ScrollArea везде, где контент может не влезть
- [ ] tests/ui/test_login.py, test_case_player.py, test_constructor.py

### ЭТАП 10 — Сборка (~3 дня)

- [ ] assets/icon.ico — создан в Этапе 0 (make_ico.py). Здесь убедиться: файл существует, размер корректный (≥30KB).
- [ ] educase.spec (PyInstaller: hidden_imports, datas, icon="assets/icon.ico")
  ```python
  # educase.spec (ключевые настройки)
  hiddenimports = [
      "PySide6.QtSvg", "PySide6.QtSvgWidgets",
      "matplotlib.backends.backend_qtagg",
      "sqlalchemy.dialects.sqlite",
      "alembic.runtime.migration",
      "bcrypt",
  ]
  datas = [
      ("assets/", "assets/"),
      ("migrations/", "migrations/"),
  ]
  # --onefile: один .exe, старт ~3-5с (распаковка во %TEMP%) — приемлемо для настольного ПО
  # Альтернатива --onedir: быстрее, но нужен инсталлятор. Выбираем onefile для простоты доставки.
  # Запускать: pyinstaller --clean --onefile --windowed educase.spec
  ```
- [ ] Тест .exe на чистой Windows 10/11 (64-bit)
- [ ] README.md, USER_GUIDE.md, CHANGELOG.md
- [ ] Inno Setup installer (.iss файл)
- [ ] ⚠️ Подпись .exe: без code signing Windows SmartScreen блокирует запуск.
      Варианты: self-signed cert (предупреждение, но не блок) или EV cert (~$300/год).
      Для внутреннего использования в ВМедА — достаточно добавить cert в доверенные через GPO.

---

## 11. МАТРИЦА ПРАВ ДОСТУПА

| Действие                      | student | teacher | admin |
| ----------------------------- | :-----: | :-----: | :---: |
| Проходить кейсы               |   ✅    |   ✅    |  ✅   |
| Личная аналитика              |   ✅    |   ✅    |  ✅   |
| Создавать/редактировать кейсы |   ❌    |   ✅    |  ✅   |
| Публиковать кейсы             |   ❌    |   ✅    |  ✅   |
| Управлять группами            |   ❌    |   ✅    |  ✅   |
| Аналитика группы              |   ❌    |   ✅    |  ✅   |
| Экспорт отчётов               |   ❌    |   ✅    |  ✅   |
| CRUD пользователей            |   ❌    |   ❌    |  ✅   |
| Управление ролями             |   ❌    |   ❌    |  ✅   |
| Системные настройки           |   ❌    |   ❌    |  ✅   |
| Бэкап/восстановление          |   ❌    |   ❌    |  ✅   |
| Системные логи                |   ❌    |   ❌    |  ✅   |

---

## 12. СТРАТЕГИЯ БЕЗОПАСНОСТИ

```python
# Пароли
bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
bcrypt.checkpw(password.encode("utf-8"), stored_hash)  # ✅ не input() — встроенная функция Python

# Сессия: singleton в памяти процесса, не персистируется
# SQL: только ORM (параметризованные запросы, нет f-strings в SQL)
# Файлы: UUID имена на диске, проверка MIME, лимиты из MEDIA_LIMITS
# Логи: user_id + action + timestamp → system_logs на каждое действие
# Блокировка: СНАЧАЛА проверяем locked_until IS NOT NULL AND locked_until > now()
#   → сразу raise AuthError("locked") БЕЗ вызова bcrypt.checkpw (bcrypt медленный)
#   Только если не заблокирован — bcrypt.checkpw(input, hash)
#   При неверном пароле: login_attempts += 1; если >= MAX_LOGIN_ATTEMPTS (=5) → locked_until = now + LOGIN_LOCKOUT_SECONDS (=300s)
# Пути: все пути через pathlib.Path, не конкатенация строк
```

---

## 13. MVP → V2 → V3

| Фича                                | MVP | V2  | V3  |
| ----------------------------------- | :-: | :-: | :-: |
| Auth 3 ролей                        | ✅  |     |     |
| SingleChoice, MultiChoice           | ✅  |     |     |
| TextInput, FormFill                 | ✅  |     |     |
| BranchingScenario (базовый, 2 пути) | ✅  |     |     |
| Плеер кейсов + FeedbackPanel        | ✅  |     |     |
| Экраны студента (все 6)             | ✅  |     |     |
| Ordering, Matching, Calculation     |     | ✅  |     |
| Timeline, TableInput                |     | ✅  |     |
| ImageAnnotation, DocumentEditor     |     | ✅  |     |
| Визуальный ScenarioBuilder          |     | ✅  |     |
| Аналитика (heatmap, charts)         |     | ✅  |     |
| Экспорт PDF/Excel                   |     | ✅  |     |
| Экраны Admin (все 5)                |     | ✅  |     |
| Тёмная тема                         |     |     | ✅  |
| Импорт/экспорт кейсов JSON          |     |     | ✅  |
| Bulk-импорт студентов CSV           |     |     | ✅  |
| DPI/масштаб HiDPI                   |     |     | ✅  |

---

## 14. ИКОНКА ПРИЛОЖЕНИЯ

### 14.1 Концепция — «Разветвлённый путь знаний»

Иконка отражает суть платформы за один взгляд: **клинический сценарий как граф принятия решений**.
Три узла (START → развилка → финал), две ветви (верная и ошибочная) — это и есть EduCase в миниатюре.

**Форма и фон:**

```
Форма:       Rounded square, радиус = 18% от размера (46px при 256px)
Фон:         radial + linear-gradient:
               radial — белый бликовый эллипс 35% 25% → transparent (glint)
               linear — #002a5e (угол) → #005bb5 (центр) → #0073d4 (ядро)
Текстура:    Hexagonal grid overlay: SVG pattern 30×34px,
               stroke rgba(255,255,255,0.035) — молекулярная/военная отсылка
Подсветка:   Левый верхний блик rgba(255,255,255,0.13) — имитация глянца
Box-shadow:  inset 0 1px 0 rgba(255,255,255,0.14) + 0 8px 40px rgba(0,40,120,0.7)
```

**Три узла графа внутри иконки (в пространстве 256×256):**

| Элемент                | Позиция                       | Форма            | Заливка                        | Обводка                      |
| ---------------------- | ----------------------------- | ---------------- | ------------------------------ | ---------------------------- |
| START-узел             | cx=128 cy=58                  | Круг r=20        | radialGradient #0b3572→#001e50 | rgba(255,255,255,0.90) 2.5px |
| ЭКГ-пульс внутри START | y=58                          | Polyline 9 точек | —                              | #5bbfff 2.2px                |
| DECISION-узел          | cx=128 cy=129                 | Ромб ±22px       | radialGradient #0b3572→#001e50 | rgba(255,255,255,0.80) 2.5px |
| «?» в ромбе            | 128,135                       | Text 20px bold   | rgba(255,255,255,0.85)         | —                            |
| SUCCESS-узел           | cx=190 cy=196                 | Круг r=17        | radialGradient #0d4a28→#071f10 | rgba(80,230,110,0.85) 2.5px  |
| Галочка ✓              | 181→188→200 / 196→203→188     | Polyline         | —                              | #4ee87a 3px                  |
| FAIL-узел              | cx=66 cy=196                  | Круг r=13        | #081628                        | rgba(255,255,255,0.22) 2px   |
| Крест ✗                | 60,190→72,202 / 72,190→60,202 | 2 линии          | —                              | rgba(255,255,255,0.28) 2.5px |

**Соединительные линии:**

```
START → DECISION:   solid,  rgba(255,255,255,0.55), 4.5px
DECISION → SUCCESS: solid,  rgba(255,255,255,0.85), 3.5px  ← яркая "верная" ветвь
DECISION → FAIL:    dashed, rgba(255,255,255,0.22), 2.5px, dasharray 7 5  ← притушенная
```

**SVG-фильтры:**

```xml
<filter id="glow">   <!-- на START и DECISION -->
  <feGaussianBlur stdDeviation="5" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="glow2">  <!-- на SUCCESS-узел -->
  <feGaussianBlur stdDeviation="4" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
```

### 14.2 Файловая структура

```
assets/
├── icon_master.svg      # Мастер-файл 256×256 viewBox="0 0 256 256"
├── icon.ico             # Мульти-размерный ICO: 256/128/64/32/16 (генерируется скриптом)
└── icon_preview.html    # Интерактивный превью всех размеров
tools/
└── make_ico.py          # Скрипт генерации .ico из SVG
```

**tools/make_ico.py:**

```python
# pip install cairosvg Pillow  (только в dev-окружении)
import cairosvg, io
from PIL import Image

SIZES = [256, 128, 64, 32, 16]

def make_ico():
    images = []
    for s in SIZES:
        png = cairosvg.svg2png(url="assets/icon_master.svg",
                               output_width=s, output_height=s)
        img = Image.open(io.BytesIO(png)).convert("RGBA")
        images.append(img)
    images[0].save(
        "assets/icon.ico", format="ICO",
        append_images=images[1:],
        sizes=[(s, s) for s in SIZES]
    )
    print(f"icon.ico создан: {SIZES}")

if __name__ == "__main__":
    make_ico()
```

> `cairosvg` — только dev-зависимость, в `requirements.txt` не входит.
> В `educase.spec` PyInstaller: `datas=[("assets/icon.ico", "assets/")]`.

---

## 15. ЗАГРУЗОЧНЫЙ ЭКРАН (SplashScreen)

### 15.1 Концепция

Тёмно-синий минималистичный экран перед `LoginWindow`.
Показывает бренд, пока в main-потоке выполняются `run_migrations()` и `build_container()`.
Гарантированное минимальное время показа: **2500ms** (даже если миграции < 200ms).

**Визуальный стиль:**

```
Размер:      540×330px, FramelessWindowHint + Qt.SplashScreen
Фон:         linear-gradient(162deg, #00122b 0%, #001e45 50%, #001535 100%)
Текстура:    Горизонтальные scanlines rgba(255,255,255,0.007) каждые 4px
Glow-ореол:  radial-gradient rgba(0,115,210,0.20) ∅300px за иконкой
Уголки:      4 corner-bracket 18×18px, #4DA3E8 @ 18% opacity
```

### 15.2 Последовательность анимации

```
Phase 1 │ 0       → 300ms  │ Окно появляется: opacity 0.0→1.0, easing OutCubic
        │                   │   QPropertyAnimation(opacity_effect, b"opacity")
─────────┼──────────────────┼──────────────────────────────────────────────────
Phase 2 │ 250ms   → 850ms  │ Иконка: scale(0.42)→scale(1.0) + opacity 0→1  ← совпадает с §16
        │                   │   easing: OutBack (c=1.70158) — эффект "пружины"
        │                   │   22 шага × ~27ms через QTimer + QPainter.scale()
─────────┼──────────────────┼──────────────────────────────────────────────────
Phase 3 │ 750ms   → 1100ms │ "EduCase" — каждая буква translateY(+18px→0) + fade
        │                   │   "Edu" — жирный, цвет #4DA3E8
        │                   │   "Case" — тонкий, белый rgba(255,255,255,0.85)
        │                   │   Stagger: 50ms между буквами (7 букв = +350ms)
─────────┼──────────────────┼──────────────────────────────────────────────────
Phase 4 │ 1200ms  → 1450ms │ Subtitle "ВМедА им. С.М. Кирова":
        │                   │   opacity 0→1 + translateY(6px→0), 250ms OutCubic
─────────┼──────────────────┼──────────────────────────────────────────────────
Phase 5 │ 1500ms  → 3800ms │ Прогресс-бар 0→100%:
        │                   │   QPropertyAnimation(progress, b"value"), 2300ms  ← T_PROGRESS_DURATION (§16)
        │                   │   easing: OutCubic (быстро до ~80%, потом замедление)
        │                   │   Цвет: gradient #005eb5 → #4DA3E8
        │                   │   Glow: box-shadow 0 0 10px rgba(77,163,232,0.55)
        │                   │   Статус: "<pulse-dot> Инициализация..."
─────────┼──────────────────┼──────────────────────────────────────────────────
Phase 6 │ 1600ms+ (фон)     │ run_migrations() + build_container()
        │                   │   app.processEvents() каждые 100ms — анимация не стопорится
─────────┼──────────────────┼──────────────────────────────────────────────────
Phase 7 │ after done        │ splash.finish(login_window):
        │                   │   opacity 1.0→0.0, 400ms InCubic
        │                   │   → splash.close() + login.show() + fade_in(login, 300ms)
```

### 15.3 Реализация — ui/windows/splash_window.py (упрощённая схема)

> ⚠️ **Размер: 540×330px** (согласован с §15.1 и §16). §16 содержит **полную продакшн-реализацию** с per-letter анимацией. Ниже — рабочая, но упрощённая версия (единый fade для заголовка).

```python
# ui/windows/splash_window.py
from PySide6.QtWidgets import (QWidget, QLabel, QProgressBar,
                                QGraphicsOpacityEffect)
from PySide6.QtCore    import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui     import QPainter, QColor, QLinearGradient, QFont
from ui.styles.animations import fade_in   # ✅ используется в start() и finish()

class SplashScreen(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.SplashScreen           # не появляется в таскбаре
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(540, 330)
        self._center_on_screen()
        self._build_ui()

    def _center_on_screen(self):
        from PySide6.QtGui import QGuiApplication
        sc = QGuiApplication.primaryScreen().geometry()
        self.move((sc.width()-540)//2, (sc.height()-330)//2)

    def _build_ui(self):
        # ── SVG-рендерер для иконки (рисуется в paintEvent через QPainter)
        from PySide6.QtSvg import QSvgRenderer
        from pathlib import Path
        _svg = Path(__file__).parent.parent.parent / "assets" / "icon_master.svg"
        self._svg_renderer = QSvgRenderer(str(_svg)) if _svg.exists() else None
        self._icon_opacity = 0.0
        self._icon_scale   = 0.45
        self._icon_step    = 0

        # ── заголовок (поверх paintEvent — используем QLabel)
        self._title = QLabel("EduCase", self)
        font = QFont("Segoe UI Variable", 28, QFont.Light)
        self._title.setFont(font)
        self._title.setStyleSheet("color: white; background: transparent;")
        self._title.adjustSize()
        self._title.move((540 - self._title.width())//2, 168)
        self._title.hide()

        # ── subtitle
        self._subtitle = QLabel("ВМедА им. С.М. Кирова", self)
        self._subtitle.setStyleSheet("""
            color: rgba(255,255,255,0.30);
            background: transparent;
            font-size: 10px;
            letter-spacing: 3px;
        """)
        self._subtitle.adjustSize()
        self._subtitle.move((540 - self._subtitle.width())//2, 210)
        self._subtitle.hide()

        # ── прогресс-бар
        self._pbar = QProgressBar(self)
        self._pbar.setGeometry(170, 282, 200, 3)   # (540-200)//2 = 170, bottom-28 = 330-48=282
        self._pbar.setTextVisible(False)
        self._pbar.setRange(0, 100)
        self._pbar.setValue(0)
        self._pbar.setStyleSheet("""
            QProgressBar {
                background: rgba(255,255,255,0.07);
                border: none; border-radius: 1px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #005eb5, stop:1 #4DA3E8);
                border-radius: 1px;
            }
        """)
        self._pbar.hide()

        # ── opacity effect на весь splash
        self._eff = QGraphicsOpacityEffect(self)
        self._eff.setOpacity(0.0)
        self.setGraphicsEffect(self._eff)

    # ─────────────────────────────────
    def start(self):
        self.show()

        # Phase 1: окно fade-in
        a = QPropertyAnimation(self._eff, b"opacity", self)
        a.setDuration(300); a.setStartValue(0.0); a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.OutCubic)
        a.start(QPropertyAnimation.DeleteWhenStopped)

        # Phase 2: иконка через 250ms
        QTimer.singleShot(250, self._start_icon_anim)

        # Phase 3: буквы через 750ms (управляются через opacity effect на title)
        QTimer.singleShot(750, lambda: (
            self._title.show(),
            self._animate_title()
        ))

        # Phase 4: subtitle через 1200ms
        QTimer.singleShot(1200, lambda: (
            self._subtitle.show(),
            fade_in(self._subtitle, 250)
        ))

        # Phase 5: progress через 1500ms
        QTimer.singleShot(1500, lambda: (
            self._pbar.show(),
            self._start_progress()
        ))

    def _start_icon_anim(self):
        self._icon_anim_t = QTimer(self)
        self._icon_anim_t.setInterval(28)
        self._icon_anim_t.timeout.connect(self._tick_icon)
        self._icon_anim_t.start()

    def _tick_icon(self):
        self._icon_step += 1
        t = min(1.0, self._icon_step / 20.0)
        # OutBack easing: c = 1.70158
        c1, c3 = 1.70158, 2.70158
        ease = 1 + c3*(t-1)**3 + c1*(t-1)**2
        self._icon_scale   = 0.45 + 0.55 * ease
        self._icon_opacity = min(1.0, t * 1.8)
        self.update()
        if self._icon_step >= 20:
            self._icon_anim_t.stop()
            self._icon_scale = 1.0
            self._icon_opacity = 1.0

    def _animate_title(self):
        # ✅ Упрощённая схема §15.3: единый fade для всего QLabel "EduCase"
        # Продакшн-версия §16 реализует per-letter анимацию через _LetterLabel + stagger
        fade_in(self._title, duration=400)  # fade_in из ui/styles/animations.py

    def _start_progress(self):
        a = QPropertyAnimation(self._pbar, b"value", self)
        a.setDuration(2300)   # ✅ T_PROGRESS_DURATION — согласовано с §16
        a.setStartValue(0); a.setEndValue(100)
        a.setEasingCurve(QEasingCurve.OutCubic)
        a.start(QPropertyAnimation.DeleteWhenStopped)

    # ─────────────────────────────────
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Фон: linear-gradient(162deg, #00122b→#001e45→#001535) как в §15.1 spec
        r = self.rect()
        rr = 18
        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        grad.setColorAt(0.0, QColor("#00122b"))
        grad.setColorAt(0.5, QColor("#001e45"))
        grad.setColorAt(1.0, QColor("#001535"))
        p.setBrush(grad)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(r, rr, rr)

        # Scanlines (лёгкая текстура)
        p.setPen(QColor(255, 255, 255, 2))
        for y in range(0, self.height(), 4):
            p.drawLine(0, y, self.width(), y)

        # Иконка с трансформацией scale
        if self._icon_opacity > 0:
            p.save()
            p.setOpacity(self._icon_opacity)
            cx, cy = (540-72)//2 + 36, 82 + 36  # центр иконки (234+36=270, 82+36=118)
            p.translate(cx, cy)
            p.scale(self._icon_scale, self._icon_scale)
            p.translate(-36, -36)
            # ✅ Рендеринг SVG иконки через QSvgRenderer
            if self._svg_renderer:
                from PySide6.QtCore import QRectF
                self._svg_renderer.render(p, QRectF(0, 0, 72, 72))
            p.restore()

    # ─────────────────────────────────
    def finish(self, login_window):
        """Phase 7: fade out → show login."""
        a = QPropertyAnimation(self._eff, b"opacity", self)
        a.setDuration(400)
        a.setStartValue(1.0); a.setEndValue(0.0)
        a.setEasingCurve(QEasingCurve.InCubic)
        a.finished.connect(lambda: (
            self.close(),
            login_window.show(),
            fade_in(login_window, 300)
        ))
        a.start()
        self._finish_anim = a  # держим ссылку
```

### 15.4 Обновлённая последовательность запуска в main.py

```python
import sys, time
from PySide6.QtWidgets import QApplication
from PySide6.QtGui     import QIcon, QFontDatabase
from PySide6.QtCore    import QTimer
from core.database     import run_migrations
from core.di_container import build_container
from core.db_maintenance import run_maintenance
from core.thread_pool  import run_async

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("EduCase")
    app.setApplicationVersion("1.0.0")

    # 0. Директории данных
    from config import _init_dirs
    _init_dirs()

    # 1. Шрифты
    QFontDatabase.addApplicationFont("assets/fonts/SegoeUIVariable.ttf")

    # 2. Показываем Splash НЕМЕДЛЕННО — до всяких тяжёлых операций
    from ui.windows.splash_window import SplashScreen
    splash = SplashScreen()
    splash.start()
    t_start = time.monotonic()
    app.processEvents()

    # 3. Миграции (sync, обычно < 200ms)
    run_migrations()
    app.processEvents()

    # 4. DI-контейнер
    container = build_container()
    app.processEvents()

    # 5. Фоновое обслуживание — отложено на 3с после старта
    QTimer.singleShot(3000, lambda: run_async(run_maintenance))

    # 6. LoginWindow — создаём заранее, не показываем
    from ui.windows.login_window import LoginWindow
    login = LoginWindow(container)

    # 7. Гарантируем минимум 2500ms показа splash
    elapsed_ms = int((time.monotonic() - t_start) * 1000)
    delay_ms   = max(0, 2500 - elapsed_ms)
    QTimer.singleShot(delay_ms, lambda: splash.finish(login))

    sys.exit(app.exec())
```

### 15.5 TODO

> Все чекпоинты по splash и иконке уже включены в **§10 Этап 0**. Не дублировать.
> Дополнительно проверить при полировке (Этап 9):
>
> - DPI 125%/150%: `QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)` до `QApplication(sys.argv)`
> - Убедиться что `QTimer.singleShot(delay_ms)` даёт ≥ 2500ms даже на медленном HDD

---

## 16. ИНСТРУКЦИЯ ДЛЯ AI-АГЕНТА: ИКОНКА И SPLASH-ЭКРАН

> **Для:** Claude Code / agentic-режим  
> **Цель:** полная интеграция иконки и загрузочного экрана в приложение  
> **Рабочая директория:** корень проекта `educase/`

---

### ШАГ 0 — Проверка исходников

```
assets/icon_master.svg   ← уже готов, не изменять
tools/make_ico.py        ← создать по инструкции ниже
```

Убедиться, что файл `assets/icon_master.svg` присутствует:

```bash
ls -lh assets/icon_master.svg
# Ожидаемый размер: ~5-6 KB
# Если файл отсутствует — это ошибка, остановиться и сообщить.
```

---

### ШАГ 1 — Сгенерировать assets/icon.ico

**1.1 Создать tools/make_ico.py:**

```python
# tools/make_ico.py
"""
Генерирует assets/icon.ico (256/128/64/32/16 px) из assets/icon_master.svg.
Запуск: python tools/make_ico.py
Dev-зависимости: pip install cairosvg Pillow
"""
import io
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent  # корень проекта

def make_ico():
    try:
        import cairosvg
        from PIL import Image
    except ImportError:
        print("Установи зависимости: pip install cairosvg Pillow")
        sys.exit(1)

    src = ROOT / "assets" / "icon_master.svg"
    dst = ROOT / "assets" / "icon.ico"

    if not src.exists():
        print(f"Файл не найден: {src}")
        sys.exit(1)

    sizes = [256, 128, 64, 32, 16]
    images = []
    for s in sizes:
        png_bytes = cairosvg.svg2png(
            url=str(src), output_width=s, output_height=s
        )
        img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        images.append(img)
        print(f"  rendered {s}x{s}")

    images[0].save(
        dst, format="ICO",
        append_images=images[1:],
        sizes=[(s, s) for s in sizes]
    )
    print(f"✅ {dst} создан ({dst.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    make_ico()
```

**1.2 Запустить:**

```bash
pip install cairosvg Pillow   # только для dev-среды
python tools/make_ico.py
# Ожидаемый вывод:
#   rendered 256x256
#   rendered 128x128
#   rendered 64x64
#   rendered 32x32
#   rendered 16x16
#   ✅ assets/icon.ico создан (N KB)
```

**1.3 Подключить иконку к приложению в main.py:**

```python
from PySide6.QtGui import QIcon
# После QApplication(sys.argv):
app.setWindowIcon(QIcon("assets/icon.ico"))
```

---

### ШАГ 2 — Создать ui/windows/splash_window.py

Создать файл **точно по коду ниже**. Не упрощать, не менять тайминги.

```python
# ui/windows/splash_window.py
"""
Загрузочный экран EduCase.
Показывается до LoginWindow, пока выполняются run_migrations() и build_container().
Гарантированное время показа: минимум 2500ms.
"""
from __future__ import annotations

from PySide6.QtCore    import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRectF
from PySide6.QtGui     import (QPainter, QColor, QLinearGradient, QRadialGradient,
                                QPen, QBrush, QFont, QFontMetrics, QGuiApplication,
                                QPixmap)
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect, QProgressBar
from pathlib import Path
BASE_DIR = Path(__file__).parent.parent.parent  # корень проекта


class SplashScreen(QWidget):
    """
    Анимированный splash-экран.

    Использование:
        splash = SplashScreen()
        splash.start()
        app.processEvents()
        # ... тяжёлые операции ...
        splash.finish(login_window)
    """

    # ── тайминги (ms) — соответствуют CSS из educase_brand_preview.html
    T_WINDOW_FADE_IN   = 300    # Phase 1
    T_ICON_START       = 200    # Phase 2: задержка до начала анимации иконки
    T_ICON_DURATION    = 650    # Phase 2: длительность "пружины"
    T_TITLE_START      = 700    # Phase 3: первая буква
    T_LETTER_STAGGER   = 50     # Phase 3: задержка между буквами
    T_SUBTITLE_START   = 1160   # Phase 4
    T_SUBTITLE_FADE    = 400    # Phase 4
    T_PROGRESS_START   = 1400   # Phase 5
    T_PROGRESS_DURATION= 2300   # Phase 5
    T_FINISH_FADE      = 400    # Phase 7

    W, H = 540, 330             # размер окна

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.SplashScreen          # не попадает в таскбар
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(self.W, self.H)
        self._center()

        # состояние иконки (анимируется через paintEvent)
        self._icon_scale   = 0.42
        self._icon_opacity = 0.0
        self._icon_step    = 0
        self._icon_svg     = self._load_icon_svg()

        # opacity effect на весь виджет
        self._eff = QGraphicsOpacityEffect(self)
        self._eff.setOpacity(0.0)
        self.setGraphicsEffect(self._eff)

        # буквы заголовка
        self._letters: list[_LetterLabel] = []

        # subtitle label
        self._subtitle_eff: QGraphicsOpacityEffect | None = None

        # прогресс-бар
        self._pbar = QProgressBar(self)
        self._pbar.setGeometry((self.W - 200) // 2, self.H - 42, 200, 3)
        self._pbar.setTextVisible(False)
        self._pbar.setRange(0, 100)
        self._pbar.setValue(0)
        self._pbar.setStyleSheet("""
            QProgressBar {
                background: rgba(255,255,255,20);
                border: none;
                border-radius: 1px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #005eb0, stop:1 #4DA3E8);
                border-radius: 1px;
            }
        """)
        self._pbar.hide()

    # ─────────────────────────────────────────
    def _center(self):
        screen = QGuiApplication.primaryScreen().geometry()
        self.move(
            (screen.width()  - self.W) // 2,
            (screen.height() - self.H) // 2,
        )

    def _load_icon_svg(self) -> QPixmap | None:
        """Загружает icon_master.svg и рендерит в QPixmap 72×72."""
        svg_path = BASE_DIR / "assets" / "icon_master.svg"
        if not svg_path.exists():
            return None
        # Рендерим SVG в QPixmap через QSvgRenderer (не QSvgWidget — тот требует родителя)
        pix = QPixmap(72, 72)
        pix.fill(Qt.transparent)
        from PySide6.QtSvg import QSvgRenderer
        svg_renderer = QSvgRenderer(str(svg_path))
        painter = QPainter(pix)
        svg_renderer.render(painter, QRectF(0, 0, 72, 72))
        painter.end()
        return pix

    # ─────────────────────────────────────────
    def start(self):
        """Показывает окно и запускает все анимации. Вызывать вместо show()."""
        self.show()

        # Phase 1: окно fade-in
        self._anim_window = QPropertyAnimation(self._eff, b"opacity", self)
        self._anim_window.setDuration(self.T_WINDOW_FADE_IN)
        self._anim_window.setStartValue(0.0)
        self._anim_window.setEndValue(1.0)
        self._anim_window.setEasingCurve(QEasingCurve.OutCubic)
        self._anim_window.start()

        # Phase 2: иконка (OutBack через ручной таймер)
        QTimer.singleShot(self.T_ICON_START, self._start_icon_anim)

        # Phase 3: буквы "EduCase" по одной
        self._build_letters()
        for i, letter in enumerate(self._letters):
            delay = self.T_TITLE_START + i * self.T_LETTER_STAGGER
            QTimer.singleShot(delay, letter.appear)

        # Phase 4: subtitle
        QTimer.singleShot(self.T_SUBTITLE_START, self._show_subtitle)

        # Phase 5: прогресс-бар
        QTimer.singleShot(self.T_PROGRESS_START, self._start_progress)

    def finish(self, login_window: QWidget):
        """Phase 7: fade out, затем показываем login."""
        anim = QPropertyAnimation(self._eff, b"opacity", self)
        anim.setDuration(self.T_FINISH_FADE)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.InCubic)
        anim.finished.connect(lambda: self._on_finish(login_window))
        anim.start()
        self._anim_finish = anim  # держим ссылку

    def _on_finish(self, login_window: QWidget):
        self.close()
        login_window.show()
        # fade-in LoginWindow
        eff = QGraphicsOpacityEffect(login_window)
        login_window.setGraphicsEffect(eff)
        eff.setOpacity(0.0)
        a = QPropertyAnimation(eff, b"opacity", login_window)
        a.setDuration(300); a.setStartValue(0.0); a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.OutCubic)
        a.start()
        login_window._splash_fade = a  # держим ссылку

    # ─────────────────────────────────────────
    def _start_icon_anim(self):
        total_steps = 22
        interval_ms = self.T_ICON_DURATION // total_steps
        self._icon_total_steps = total_steps
        t = QTimer(self)
        t.setInterval(interval_ms)
        t.timeout.connect(self._tick_icon)
        t.start()
        self._icon_timer = t

    def _tick_icon(self):
        self._icon_step += 1
        t = min(1.0, self._icon_step / self._icon_total_steps)
        # OutBack easing
        c1, c3 = 1.70158, 2.70158
        ease = 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
        self._icon_scale   = max(0.0, 0.42 + 0.58 * ease)
        self._icon_opacity = min(1.0, t * 1.8)
        self.update()  # trigger paintEvent
        if self._icon_step >= self._icon_total_steps:
            self._icon_timer.stop()
            self._icon_scale, self._icon_opacity = 1.0, 1.0
            self.update()

    # ─────────────────────────────────────────
    def _build_letters(self):
        """Создаёт QWidget-метки для каждой буквы 'EduCase'."""
        text   = "EduCase"
        bold   = "Edu"
        font_b = QFont("Segoe UI Variable", 26, QFont.DemiBold)
        font_n = QFont("Segoe UI Variable", 26, QFont.Light)

        # Вычисляем суммарную ширину для центрирования
        total_w = 0
        widths  = []
        for ch in text:
            f = font_b if ch in bold else font_n
            w = QFontMetrics(f).horizontalAdvance(ch) + 1
            widths.append(w)
            total_w += w

        x = (self.W - total_w) // 2
        # Иконка 72px + margin 16 + (нижняя часть иконки) → ~168px от верха
        y = 172

        for i, ch in enumerate(text):
            f   = font_b if ch in bold else font_n
            col = QColor("#4DA3E8") if ch in bold else QColor(255, 255, 255, 220)
            lbl = _LetterLabel(ch, f, col, self)
            lbl.move(x, y)
            lbl.resize(widths[i], 52)   # ✅ 52px: хватает для text baseline + y_offset=22
            lbl.hide()
            self._letters.append(lbl)
            x += widths[i]

    def _show_subtitle(self):
        from PySide6.QtWidgets import QLabel
        sub = QLabel("ВМедА им. С.М. Кирова", self)
        sub.setStyleSheet("""
            color: rgba(255,255,255,80);
            background: transparent;
            font-size: 9px;
            letter-spacing: 3px;
        """)
        sub.adjustSize()
        sub.move((self.W - sub.width()) // 2, 222)

        eff = QGraphicsOpacityEffect(sub)
        sub.setGraphicsEffect(eff)
        eff.setOpacity(0.0)
        sub.show()

        a = QPropertyAnimation(eff, b"opacity", sub)
        a.setDuration(self.T_SUBTITLE_FADE)
        a.setStartValue(0.0); a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.OutCubic)
        a.start()
        sub._anim = a  # держим ссылку
        self._subtitle_widget = sub

    def _start_progress(self):
        self._pbar.show()
        a = QPropertyAnimation(self._pbar, b"value", self)
        a.setDuration(self.T_PROGRESS_DURATION)
        a.setStartValue(0); a.setEndValue(100)
        a.setEasingCurve(QEasingCurve.OutCubic)
        a.start()
        self._anim_progress = a

    # ─────────────────────────────────────────
    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        r  = self.rect()
        rr = 18  # corner radius

        # ── фон: тёмно-синий градиент
        grad = QLinearGradient(0, 0, r.width() * 0.6, r.height())
        grad.setColorAt(0.0, QColor("#00122b"))
        grad.setColorAt(0.5, QColor("#001e45"))
        grad.setColorAt(1.0, QColor("#001535"))
        p.setBrush(grad)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(r, rr, rr)

        # ── scanlines (лёгкая текстура)
        p.setPen(QPen(QColor(255, 255, 255, 2), 1))
        for y in range(0, self.H, 4):
            p.drawLine(0, y, self.W, y)

        # ── радиальный ореол за иконкой
        halo = QRadialGradient(self.W / 2, self.H / 2 - 20, 150)
        halo.setColorAt(0.0, QColor(0, 115, 212, 46))
        halo.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(halo)
        p.drawEllipse(self.W//2 - 150, self.H//2 - 170, 300, 300)

        # ── corner brackets (декоративные уголки)
        pen_corner = QPen(QColor(77, 163, 232, 46), 1.5)
        p.setPen(pen_corner)
        p.setBrush(Qt.NoBrush)
        d, sz = 16, 18  # отступ и длина уголка
        for (x1,y1, dx,dy) in [
            (d, d,       sz, 0), (d,      d, 0, sz),    # top-left
            (self.W-d-sz, d,   sz, 0), (self.W-d, d, 0, sz),   # top-right
            (d, self.H-d-sz, sz, 0), (d, self.H-d, 0, -sz),   # bottom-left (fix)
            (self.W-d-sz, self.H-d, sz, 0), (self.W-d, self.H-d, 0, -sz), # bottom-right
        ]:
            # Рисуем линии уголков через координаты
            pass
        # Упрощённые уголки через drawLine
        cp = QPen(QColor(77, 163, 232, 46), 1.5)
        p.setPen(cp)
        sz2 = 18
        # TL
        p.drawLine(d, d, d+sz2, d); p.drawLine(d, d, d, d+sz2)
        # TR
        p.drawLine(self.W-d, d, self.W-d-sz2, d); p.drawLine(self.W-d, d, self.W-d, d+sz2)
        # BL
        p.drawLine(d, self.H-d, d+sz2, self.H-d); p.drawLine(d, self.H-d, d, self.H-d-sz2)
        # BR
        p.drawLine(self.W-d, self.H-d, self.W-d-sz2, self.H-d)
        p.drawLine(self.W-d, self.H-d, self.W-d, self.H-d-sz2)

        # ── иконка (SVG pixmap с анимируемым scale и opacity)
        if self._icon_svg and self._icon_opacity > 0.01:
            p.save()
            p.setOpacity(self._icon_opacity)
            # Центр иконки: 72px квадрат
            cx = (self.W - 72) // 2 + 36   # = 270
            cy = 88 + 36                     # = 124
            p.translate(cx, cy)
            p.scale(self._icon_scale, self._icon_scale)
            p.translate(-36, -36)
            p.drawPixmap(0, 0, self._icon_svg)
            p.restore()

        # ── рамка (тонкая, поверх всего)
        p.setPen(QPen(QColor(255, 255, 255, 18), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(0.5, 0.5, self.W - 1, self.H - 1, rr, rr)


# ✅ Property вынесен на уровень модуля (не внутри класса — нестандартно)
from PySide6.QtCore import Property as _QtProp

class _LetterLabel(QWidget):
    """Одна буква заголовка с анимацией появления снизу."""

    def __init__(self, char: str, font: QFont, color: QColor, parent):
        super().__init__(parent)
        self._char  = char
        self._font  = font
        self._color = color
        self._y_offset = 22.0   # начальный сдвиг вниз (px)
        self._opacity  = 0.0
        self.setAttribute(Qt.WA_TranslucentBackground)

    def appear(self):
        self.show()
        # ✅ QPropertyAnimation требует Qt Property (через @Property decorator)
        # Таргеты b"y_offset" и b"letter_opacity" совпадают с именами @Property ниже
        self._anim_y = QPropertyAnimation(self, b"y_offset", self)
        self._anim_y.setDuration(380)
        self._anim_y.setStartValue(22.0); self._anim_y.setEndValue(0.0)
        self._anim_y.setEasingCurve(QEasingCurve.OutCubic)
        self._anim_y.start()

        self._anim_o = QPropertyAnimation(self, b"letter_opacity", self)
        self._anim_o.setDuration(380)
        self._anim_o.setStartValue(0.0); self._anim_o.setEndValue(1.0)
        self._anim_o.setEasingCurve(QEasingCurve.OutCubic)
        self._anim_o.start()

    # ✅ Qt Property — имя свойства совпадает с аргументом b"..." в QPropertyAnimation
    def _get_y_offset(self):    return self._y_offset
    def _set_y_offset(self, v): self._y_offset = v; self.update()
    y_offset = _QtProp(float, _get_y_offset, _set_y_offset)   # таргет: b"y_offset"

    def _get_opacity(self):     return self._opacity
    def _set_opacity(self, v):  self._opacity = v; self.update()
    letter_opacity = _QtProp(float, _get_opacity, _set_opacity)  # таргет: b"letter_opacity"

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.setOpacity(self._opacity)
        p.setFont(self._font)
        p.setPen(self._color)
        p.drawText(0, int(self._y_offset) + 34, self._char)
```

**Важно после создания файла:**

```bash
# Убедиться что PySide6.QtSvg установлен (входит в PySide6):
python -c "from PySide6.QtSvg import QSvgRenderer; print('OK')"
# QSvgWidget не используется в splash_window.py — не нужно импортировать
```

---

### ШАГ 3 — Обновить main.py

Найти существующий `main.py` и заменить launch-последовательность:

```python
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtGui     import QIcon, QFontDatabase
from PySide6.QtCore    import QTimer
import sys

from config                    import _init_dirs
from core.database             import run_migrations
from core.di_container         import build_container
from core.db_maintenance       import run_maintenance
from core.thread_pool          import run_async
from ui.windows.splash_window  import SplashScreen


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("EduCase")
    app.setApplicationVersion("1.0.0")

    # Иконка приложения (таскбар + Alt+Tab)
    app.setWindowIcon(QIcon("assets/icon.ico"))

    # 0. Директории данных
    _init_dirs()

    # 1. Шрифты
    QFontDatabase.addApplicationFont("assets/fonts/SegoeUIVariable.ttf")

    # 2. Splash — показываем НЕМЕДЛЕННО
    splash = SplashScreen()
    splash.start()
    t0 = time.monotonic()
    app.processEvents()

    # 3. Миграции (sync, обычно < 200ms)
    run_migrations()
    app.processEvents()

    # 4. DI-контейнер
    container = build_container()
    app.processEvents()

    # 5. Фоновое обслуживание — после старта
    QTimer.singleShot(3000, lambda: run_async(run_maintenance))

    # 6. LoginWindow — создаём заранее, не показываем
    from ui.windows.login_window import LoginWindow
    login = LoginWindow(container)

    # 7. Гарантируем минимум 2500ms показа splash
    elapsed = int((time.monotonic() - t0) * 1000)
    delay   = max(0, 2500 - elapsed)
    QTimer.singleShot(delay, lambda: splash.finish(login))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

### ШАГ 4 — Обновить educase.spec (PyInstaller)

В секцию `datas` добавить:

```python
datas = [
    ("assets/",     "assets/"),      # включает icon.ico и icon_master.svg
    ("migrations/", "migrations/"),
]
hiddenimports = [
    "PySide6.QtSvg",
    "PySide6.QtSvgWidgets",
    "PySide6.QtCore",
    "matplotlib.backends.backend_qtagg",
    "sqlalchemy.dialects.sqlite",
    "alembic.runtime.migration",
    "bcrypt",
]
```

---

### ШАГ 5 — Проверка

```bash
# Быстрый smoke-test splash без запуска всего приложения:
python - << 'EOF'
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore    import QTimer
from ui.windows.splash_window import SplashScreen

app = QApplication(sys.argv)
splash = SplashScreen()
splash.start()
QTimer.singleShot(4000, app.quit)   # закрыть через 4 секунды
sys.exit(app.exec())
EOF
```

Ожидаемое поведение:

1. Тёмно-синий экран 540×330 появляется в центре
2. Иконка "пружинит" из центра (scale 0.42 → 1.0)
3. Буквы "EduCase" поднимаются по одной
4. Subtitle появляется снизу
5. Прогресс-бар заполняется ~2.3 секунды
6. Через 4с окно закрывается

---

### Известные ограничения Qt vs HTML

| Эффект в HTML                      | Аналог в Qt                                                             | Точность |
| ---------------------------------- | ----------------------------------------------------------------------- | -------- |
| SVG `feGaussianBlur` glow на узлах | `QGraphicsDropShadowEffect` или рисовать в `paintEvent`                 | ~85%     |
| CSS hex-texture `::before`         | `QPixmap` + тайлинг в `paintEvent`                                      | 100%     |
| CSS `letter-spacing`               | `QFont.setLetterSpacing()`                                              | 100%     |
| CSS `translateY` на буквах         | `_LetterLabel.y_offset` property + `QPainter`                           | 100%     |
| CSS `radial-gradient` halo         | `QRadialGradient` в `paintEvent`                                        | 95%      |
| Прогресс-бар glow                  | `QSS box-shadow` не поддерживается → рисовать поверх через `paintEvent` | 70%      |

> **Про glow на прогресс-баре:** если нужен точный эффект — создать `_GlowProgressBar(QWidget)` и рисовать вручную через `QPainter + QRadialGradient` вместо стандартного `QProgressBar`.

---

_EduCase Project Design v2.0 — Полный аудит | 2026-03-04_
