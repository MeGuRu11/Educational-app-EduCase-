# core/validators.py
"""
Валидаторы данных форм.
Используются в сервисах и презентерах для проверки пользовательского ввода.
"""
from __future__ import annotations

import re
from pathlib import Path

from core.exceptions import MediaError, ValidationError
from config import MEDIA_LIMITS


def validate_username(username: str) -> str:
    """
    Логин: [a-zA-Z0-9_], 3–30 символов.
    Возвращает очищенный username или raises ValidationError.
    """
    username = username.strip()
    if not username:
        raise ValidationError("Логин не может быть пустым", field="username")
    if len(username) < 3:
        raise ValidationError("Логин должен быть не короче 3 символов", field="username")
    if len(username) > 30:
        raise ValidationError("Логин должен быть не длиннее 30 символов", field="username")
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        raise ValidationError(
            "Логин может содержать только латинские буквы, цифры и _", field="username"
        )
    return username


def validate_password(password: str) -> str:
    """
    Пароль: ≥8 символов, ≥1 цифра.
    Возвращает пароль или raises ValidationError.
    """
    if len(password) < 8:
        raise ValidationError("Пароль должен быть не короче 8 символов", field="password")
    if not re.search(r"\d", password):
        raise ValidationError("Пароль должен содержать хотя бы одну цифру", field="password")
    return password


def validate_full_name(full_name: str) -> str:
    """ФИО: непустое, 2–100 символов."""
    full_name = full_name.strip()
    if not full_name:
        raise ValidationError("ФИО не может быть пустым", field="full_name")
    if len(full_name) < 2:
        raise ValidationError("ФИО должно быть не короче 2 символов", field="full_name")
    if len(full_name) > 100:
        raise ValidationError("ФИО должно быть не длиннее 100 символов", field="full_name")
    return full_name


def validate_image(path: Path, media_type: str) -> None:
    """
    Проверяет файл изображения: размер + MIME через Pillow.
    media_type: 'cover' | 'task_image' | 'avatar'
    """
    limits = MEDIA_LIMITS.get(media_type)
    if not limits:
        raise MediaError(f"Неизвестный тип медиа: {media_type}")

    if not path.exists():
        raise MediaError(f"Файл не найден: {path}")

    file_size = path.stat().st_size
    if file_size > limits["max_bytes"]:
        max_mb = limits["max_bytes"] / (1024 * 1024)
        raise MediaError(f"Файл слишком большой: {file_size} байт (макс. {max_mb:.1f} MB)")

    ext = path.suffix.lower().lstrip(".")
    if ext not in limits["formats"]:
        raise MediaError(
            f"Неподдерживаемый формат: .{ext} (допустимо: {', '.join(limits['formats'])})"
        )

    # Проверка через Pillow — файл реально является изображением
    try:
        from PIL import Image

        img = Image.open(path)
        img.verify()
    except Exception:
        raise MediaError(f"Файл повреждён или не является изображением: {path.name}")
