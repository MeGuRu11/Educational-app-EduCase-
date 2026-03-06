# services/seed.py
"""
Инициализация базы данных: роли, админ, тестовые пользователи и дисциплины.
"""
import json
from loguru import logger  # type: ignore
from sqlalchemy.orm import Session

from models.user import Role, User
from services.user_service import UserService
from repositories.user_repo import UserRepository, RoleRepository


def seed_database(session: Session) -> None:
    role_repo = RoleRepository(session)
    user_repo = UserRepository(session)
    user_service = UserService(user_repo, role_repo)

    # 1. Роли
    roles_data = [
        {
            "name": "admin",
            "display_name": "Администратор",
            "permissions": json.dumps({"all": True})
        },
        {
            "name": "teacher",
            "display_name": "Преподаватель",
            "permissions": json.dumps({
                "cases.create": True,
                "cases.edit": True,
                "groups.manage": True,
                "reports.view": True
            })
        },
        {
            "name": "student",
            "display_name": "Обучающийся",
            "permissions": json.dumps({
                "cases.pass": True,
                "reports.own": True
            })
        }
    ]

    # Сначала пытаемся создать роли
    for rd in roles_data:
        if not role_repo.get_by_name(rd["name"]):
            role_repo.create(**rd)
            logger.info(f"Создана роль: {rd['name']}")

    # 2. Пользователи
    users_data = [
        ("admin", "admin_pass", "Администратор Системы", "admin"),
        ("teacher1", "12345", "Иванов И.И.", "teacher"),
        ("student1", "12345", "Петров П.П.", "student"),
    ]

    for un, pw, fn, rn in users_data:
        if not user_repo.get_by_username(un):
            user_service.create_user(un, pw, fn, rn)
            logger.info(f"Создан тестовый пользователь: {un}")

    logger.info("Завершено сидирование базы данных")

if __name__ == "__main__":
    from core.database import Session as DBSession
    with DBSession() as session:
        seed_database(session)
