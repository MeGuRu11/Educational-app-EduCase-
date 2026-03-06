# services/auth_service.py
"""
Сервис аутентификации.
Работает с UserRepository. bcrypt для хэшей, блокировка при login_attempts >= 5.
"""
from datetime import datetime, timedelta
import bcrypt
from loguru import logger

import app  # Используем app.py как модульный синглтон
from config import LOGIN_LOCKOUT_SECONDS, MAX_LOGIN_ATTEMPTS
from core.exceptions import AuthError
from core.event_bus import bus
from models.user import User
from repositories.user_repo import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def login(self, username: str, password: str) -> User:
        user = self.user_repo.get_by_username(username)

        # 1. Формальная проверка существования и активности (задержка чтобы не дать timing attack на username)
        if not user or not user.is_active:
            # Делаем dummy check для защиты от timing-атаки
            bcrypt.checkpw(password.encode(), b"$2b$12$KIXeW3H0g0Z3M5.dJ/H95ui5X2E5jI2G6l3Q1M9S9Zp/y7o0aB1X.")
            raise AuthError("Неверный логин или пароль", "INVALID_CREDENTIALS")

        current_time = datetime.utcnow()

        # 2. Проверка lockout (блокировки по попыткам)
        if user.locked_until:
            locked_until = datetime.fromisoformat(user.locked_until)
            if current_time < locked_until:
                remaining = int((locked_until - current_time).total_seconds())
                logger.warning(f"Попытка входа заблокированного пользователя: {username}")
                raise AuthError(
                    f"Учётная запись заблокирована. Повторите через {remaining} сек.",
                    "ACCOUNT_LOCKED"
                )
            else:
                # Время блокировки истекло — сбрасываем счётчик
                self._reset_attempts(user)

        # 3. Проверка пароля (bcrypt)
        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            self._increment_attempts(user)
            logger.warning(f"Неудачная попытка входа: {username} ({user.login_attempts}/{MAX_LOGIN_ATTEMPTS})")
            
            if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
                logger.error(f"Учётная запись заблокирована из-за множества неудачных попыток: {username}")
                raise AuthError("Превышено число попыток. Блокировка на 5 минут.", "LOCKED_OUT")
                
            raise AuthError("Неверный логин или пароль", "INVALID_CREDENTIALS")

        # 4. Успешно
        self._reset_attempts(user)
        user.last_login_at = current_time.isoformat()
        self.user_repo.update(user)
        
        # 5. Установка глобального состояния
        app.current_user = user
        logger.info(f"Успешный вход: {username} (Роль: {user.role.name})")
        
        # 6. Эмитируем сигнал
        bus.user_logged_in.emit(user)
        
        return user

    def logout(self) -> None:
        user = app.current_user
        if user:
            logger.info(f"Выход из системы: {user.username}")
            app.current_user = None
            bus.user_logged_out.emit()

    def check_permission(self, required_perm: str) -> bool:
        """Проверяет флаг пермиссии у текущего пользователя (JSON role.permissions)."""
        user = app.current_user
        if not user:
            return False
            
        perms = user.role.permissions_dict
        
        # admin имеет полный доступ ко всему
        if user.role.name == "admin":
            return True
            
        # конкретная пермиссия, или wildcard для модуля (напр., tasks.*)
        if perms.get(required_perm, False):
            return True
            
        module = required_perm.split(".")[0]
        if perms.get(f"{module}.*", False):
            return True
            
        return False

    def _increment_attempts(self, user: User) -> None:
        user.login_attempts += 1
        if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
            lockout_time = datetime.utcnow() + timedelta(seconds=LOGIN_LOCKOUT_SECONDS)
            user.locked_until = lockout_time.isoformat()
        self.user_repo.update(user)

    def _reset_attempts(self, user: User) -> None:
        if user.login_attempts > 0 or user.locked_until:
            user.login_attempts = 0
            user.locked_until = None
            self.user_repo.update(user)
