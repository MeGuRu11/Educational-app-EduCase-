# tests/unit/test_auth.py
"""
Юнит тесты для AuthService.
Проверка логина, блокировок, bcrypt.
"""
from datetime import datetime, timedelta
import pytest

from core.exceptions import AuthError
from config import MAX_LOGIN_ATTEMPTS, LOGIN_LOCKOUT_SECONDS


def test_login_success(auth_service, seed_users):
    user = auth_service.login("test_user", "test_pass")
    assert user is not None
    assert user.username == "test_user"
    assert user.login_attempts == 0
    assert user.locked_until is None


def test_login_invalid_password(auth_service, seed_users):
    with pytest.raises(AuthError) as excinfo:
        auth_service.login("test_user", "wrong_pass")
    assert excinfo.value.code == "INVALID_CREDENTIALS"

    # Проверяем, что попытка записалась
    user = auth_service.user_repo.get_by_username("test_user")
    assert user.login_attempts == 1


def test_login_non_existent_user(auth_service, seed_users):
    with pytest.raises(AuthError) as excinfo:
        auth_service.login("no_such_user", "password")
    assert excinfo.value.code == "INVALID_CREDENTIALS"


def test_login_lockout(auth_service, seed_users):
    # Провалить вход MAX_LOGIN_ATTEMPTS раз
    for i in range(MAX_LOGIN_ATTEMPTS - 1):
        with pytest.raises(AuthError) as excinfo:
            auth_service.login("test_user", "wrong_pass")
        assert excinfo.value.code == "INVALID_CREDENTIALS"
        
    # На последней попытке ловим блокировку
    with pytest.raises(AuthError) as excinfo:
        auth_service.login("test_user", "wrong_pass")
    
    assert excinfo.value.code == "LOCKED_OUT"
    
    user = auth_service.user_repo.get_by_username("test_user")
    assert user.login_attempts == MAX_LOGIN_ATTEMPTS
    assert user.locked_until is not None
    
    # Теперь даже с правильным паролем должна быть ошибка Account Locked
    with pytest.raises(AuthError) as excinfo:
        auth_service.login("test_user", "test_pass")
    assert excinfo.value.code == "ACCOUNT_LOCKED"


def test_lockout_expires(auth_service, seed_users):
    # Устанавливаем блокировку вручную в прошлом
    user = auth_service.user_repo.get_by_username("test_user")
    user.login_attempts = MAX_LOGIN_ATTEMPTS
    
    past_time = datetime.utcnow() - timedelta(seconds=LOGIN_LOCKOUT_SECONDS + 10)
    user.locked_until = past_time.isoformat()
    auth_service.user_repo.update(user)
    
    # Вход должен пройти успешно и сбросить блокировку
    logged_in_user = auth_service.login("test_user", "test_pass")
    
    assert logged_in_user.login_attempts == 0
    assert logged_in_user.locked_until is None
