# services/user_service.py
"""
Сервис для управления пользователями (CRUD и бизнес-логика).
"""
import bcrypt
from loguru import logger

from core.exceptions import AppError
from models.user import User
from repositories.user_repo import UserRepository, RoleRepository


class UserService:
    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository):
        self.user_repo = user_repo
        self.role_repo = role_repo

    def create_user(
        self, username: str, password: str, full_name: str, role_name: str, group_id: int | None = None
    ) -> User:
        # Проверка роли
        role = self.role_repo.get_by_name(role_name)
        if not role:
            raise AppError(f"Роль '{role_name}' не найдена", "ROLE_NOT_FOUND")

        # Проверка уникальности
        existing = self.user_repo.get_by_username(username)
        if existing:
            raise AppError(f"Пользователь '{username}' уже существует", "USER_EXISTS")

        # Хэширование
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

        # Создание
        user = self.user_repo.create(
            username=username,
            password_hash=password_hash,
            full_name=full_name,
            role_id=role.id,
            group_id=group_id,
        )
        logger.info(f"Создан пользователь: {username} (Роль: {role_name})")
        return user

    def change_password(self, user_id: int, new_password: str) -> User:
        user = self.user_repo.get(user_id)
        if not user:
            raise AppError("Пользователь не найден", "USER_NOT_FOUND")

        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(new_password.encode("utf-8"), salt).decode("utf-8")
        
        user = self.user_repo.update(user, password_hash=password_hash)
        logger.info(f"Пароль изменён для пользователя: {user.username}")
        return user
