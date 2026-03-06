# core/di_container.py
"""
Простой DI-контейнер: все зависимости собираются здесь один раз при старте.
Repositories и Services — STATELESS синглтоны.
Состояние (current_user, config) хранится в app.py, НЕ в сервисах.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Container:
    """DI-контейнер: хранит все репозитории и сервисы."""

    # Repositories
    user_repo: Any = None
    group_repo: Any = None
    case_repo: Any = None
    module_repo: Any = None
    task_repo: Any = None
    scenario_repo: Any = None
    attempt_repo: Any = None
    media_repo: Any = None
    analytics_repo: Any = None

    # Services
    auth_service: Any = None
    user_service: Any = None
    group_service: Any = None
    case_service: Any = None
    module_service: Any = None
    task_service: Any = None
    media_service: Any = None
    grader_service: Any = None
    scenario_service: Any = None
    attempt_service: Any = None
    analytics_service: Any = None
    export_service: Any = None
    backup_service: Any = None


def build_container() -> Container:
    """
    Собирает все зависимости. Вызывается из main.py один раз при старте.

    Порядок: сначала repos (stateless), затем services (получают repos как аргументы).
    Конкретные классы импортируются здесь — ленивая загрузка.
    """
    c = Container()

    # ── Repositories ──────────────────────────────────────────────────────
    from app import get_session
    from repositories.user_repo import RoleRepository, UserRepository
    from repositories.group_repo import GroupRepository

    # Используем одну "синглтон-сессию" для DI или получаем её на лету
    # Здесь для упрощения мы инжектим функцию получения сессии, так как репозитории 
    # в нашей архитектуре принимают сессию в конструкторе
    session = get_session()
    
    role_repo = RoleRepository(session)
    user_repo = UserRepository(session)
    group_repo = GroupRepository(session)
    
    c.user_repo = user_repo
    c.group_repo = group_repo
    
    # ── Services ──────────────────────────────────────────────────────────
    from services.auth_service import AuthService
    from services.user_service import UserService
    
    user_service = UserService(user_repo, role_repo)
    c.user_service = user_service
    
    c.auth_service = AuthService(user_repo)

    return c
