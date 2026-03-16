from PySide6.QtCore import QObject, QTimer, Qt, QEvent
from PySide6.QtWidgets import QApplication

from core.event_bus import bus
import app

class IdleGuard(QObject):
    """
    Отслеживает бездействие пользователя. 
    При отсутствии активности мыши/клавиатуры отправляет события:
    - `bus.idle_warning` (за N мс до логаута - показываем диалог)
    - `bus.idle_timeout` (логаут)
    """
    def __init__(self, warn_ms: int = 14 * 60 * 1000, timeout_ms: int = 15 * 60 * 1000, parent=None):
        super().__init__(parent)
        self.warn_ms = warn_ms
        self.timeout_ms = timeout_ms

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        
        self._last_activity = 0
        self._warning_emitted = False
        self._is_running = False

    def start(self):
        self._is_running = True
        self._warning_emitted = False
        self.reset_idle()
        self._timer.start(1000) # Проверка каждую секунду
        
        # Перехватываем события активности на уровне приложения
        qapp = QApplication.instance()
        if qapp:
            qapp.installEventFilter(self)

    def stop(self):
        self._is_running = False
        self._timer.stop()
        
        qapp = QApplication.instance()
        if qapp:
            qapp.removeEventFilter(self)

    def reset_idle(self):
        """Сбрасывает таймер неактивности."""
        import time
        self._last_activity = int(time.time() * 1000)
        self._warning_emitted = False

    def eventFilter(self, obj, event):
        """Фильтруем события мыши, клавиатуры и тача для сброса таймера."""
        if not self._is_running or not app.current_user:
            return False

        if event.type() in (
            QEvent.Type.MouseMove,
            QEvent.Type.MouseButtonPress,
            QEvent.Type.MouseButtonRelease,
            QEvent.Type.MouseButtonDblClick,
            QEvent.Type.KeyPress,
            QEvent.Type.KeyRelease,
            QEvent.Type.Wheel,
            QEvent.Type.TouchBegin,
            QEvent.Type.TouchUpdate
        ):
            self.reset_idle()

        return False # Не блокируем событие

    def _on_tick(self):
        if not self._is_running or not app.current_user:
            return

        import time
        now = int(time.time() * 1000)
        idle_time = now - self._last_activity

        if idle_time >= self.timeout_ms:
            self.stop() # Чтобы не спамить логаутами
            bus.emit("idle_timeout", None)
            
        elif idle_time >= self.warn_ms and not self._warning_emitted:
            self._warning_emitted = True
            left_seconds = (self.timeout_ms - idle_time) // 1000
            bus.emit("idle_warning", left_seconds)
