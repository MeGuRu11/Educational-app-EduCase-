# core/event_bus.py
"""
Qt EventBus singleton.
Все модули общаются через сигналы — нет прямых зависимостей между UI-компонентами.
⚠️ QApplication должен быть создан ДО импорта этого модуля.
"""
from PySide6.QtCore import QObject, Signal


class EventBus(QObject):
    # Auth
    user_logged_in = Signal(object)  # User
    user_logged_out = Signal()

    # Navigation
    navigate_to = Signal(str, object)  # screen_name, kwargs dict
    start_case = Signal(int)  # case_id

    # Notifications
    show_toast = Signal(str, str)  # message, level ("success"/"error"/"info"/"warning")

    # Content updates
    case_published = Signal(int)  # case_id
    attempt_finished = Signal(int)  # attempt_id
    user_updated = Signal(int)  # user_id

    _instance = None

    @classmethod
    def instance(cls) -> "EventBus":
        if not cls._instance:
            cls._instance = cls()
        return cls._instance


bus = EventBus.instance()
