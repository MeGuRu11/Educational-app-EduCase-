# core/exceptions.py
"""
Иерархия ошибок приложения EduCase.
AppError(Exception)
├─ AuthError        (неверный пароль / заблокирован)
├─ PermissionError  (нет прав)
├─ NotFoundError    (объект не найден в БД)
├─ ValidationError  (неверные данные формы)
└─ MediaError       (файл слишком большой / неверный тип)
"""


class AppError(Exception):
    """Базовая ошибка приложения."""

    def __init__(self, message: str = "", code: str = ""):
        self.message = message
        self.code = code
        super().__init__(message)


class AuthError(AppError):
    """Ошибка аутентификации: неверный пароль, заблокирован, неактивен."""
    pass


class PermissionDeniedError(AppError):
    """Нет прав для выполнения операции."""
    pass


class NotFoundError(AppError):
    """Объект не найден в базе данных."""
    pass


class ValidationError(AppError):
    """Неверные данные формы или бизнес-правило нарушено."""

    def __init__(self, message: str = "", code: str = "", field: str = ""):
        super().__init__(message, code)
        self.field = field


class MediaError(AppError):
    """Ошибка медиафайла: слишком большой, неверный MIME-тип, повреждён."""
    pass
