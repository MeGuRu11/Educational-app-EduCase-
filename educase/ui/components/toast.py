# ui/components/toast.py
"""
Toast Manager и кастомный виджет уведомлений.
Отображает всплывающие сообщения поверх главного окна.
Типы: info, success, warning, error.
"""
from typing import Literal, List, Optional

from PySide6.QtCore import QPoint, QPropertyAnimation, QTimer, Qt, QEasingCurve
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGraphicsOpacityEffect

from core.event_bus import bus
from ui.styles.animations import fade_in, fade_out
from ui.styles.icons import get_icon
from ui.styles.theme import ANIM, COLORS, RADIUS


class Toast(QWidget):
    """Одиночное всплывающее уведомление."""
    
    def __init__(
        self,
        parent: Optional[QWidget],
        message: str,
        type_: Literal["info", "success", "warning", "error"] = "info",
        duration_ms: int = 4000
    ):
        super().__init__(parent)
        self.message = message
        self.type_ = type_
        self.duration_ms = duration_ms
        
        self.anim_opacity: QPropertyAnimation | None = None
        self._pos_anim: QPropertyAnimation | None = None
        
        # Настройка цветов в зависимости от типа
        self.bg_color = QColor(COLORS[f"{type_}_bg"])
        self.text_color = QColor(COLORS[type_])
        if type_ == "info":
            # special case for info
            self.bg_color = QColor(COLORS["bg_elevated"])
            self.text_color = QColor(COLORS["text_primary"])
            
        self._setup_ui()
        
        # Настройка эффекта прозрачности
        self.effect = QGraphicsOpacityEffect(self)
        self.effect.setOpacity(0.0)
        self.setGraphicsEffect(self.effect)
        
        # Таймер скрытия
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_animated)

    def _setup_ui(self) -> None:
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        self.label = QLabel(self.message, self)
        font = QFont("Segoe UI Variable", 11)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label.setStyleSheet(f"color: {self.text_color.name()}; background: transparent;")
        
        layout.addWidget(self.label)
        self.adjustSize()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем фон со скруглениями
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), RADIUS["card"], RADIUS["card"])
        p.fillPath(path, self.bg_color)
        
        # Рамка
        p.setPen(QColor(COLORS["stroke_card"]))
        p.drawPath(path)

    def show_animated(self) -> None:
        self.show()
        # Slide up & Fade in
        self.anim_opacity = QPropertyAnimation(self.effect, b"opacity", self)
        self.anim_opacity.setDuration(ANIM["medium"])
        self.anim_opacity.setStartValue(0.0)
        self.anim_opacity.setEndValue(1.0)
        self.anim_opacity.setEasingCurve(QEasingCurve.Type.OutExpo)
        self.anim_opacity.start()
        
        # Автоматическое скрытие
        if self.duration_ms > 0:
            self.hide_timer.start(self.duration_ms)

    def hide_animated(self) -> None:
        self.anim_opacity = QPropertyAnimation(self.effect, b"opacity", self)
        self.anim_opacity.setDuration(ANIM["medium"])
        self.anim_opacity.setStartValue(1.0)
        self.anim_opacity.setEndValue(0.0)
        self.anim_opacity.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim_opacity.finished.connect(self.deleteLater)
        self.anim_opacity.start()


class ToastManager:
    """Глобальный менеджер тостов. Подписывается на EventBus."""
    
    def __init__(self, main_window: Optional[QWidget] = None):
        self.main_window = main_window
        self.active_toasts: List[Toast] = []
        
        bus.show_toast.connect(self.show_toast)

    def show_toast(self, message: str, type_: Literal["info", "success", "warning", "error"] = "info") -> None:
        if not self.main_window:
            return
            
        duration = 6000 if type_ == "error" else 4000
        toast = Toast(self.main_window, message, type_, duration)
        
        self.active_toasts.append(toast)
        toast.destroyed.connect(lambda: self._on_toast_destroyed(toast))
        
        self._layout_toasts()
        toast.show_animated()

    def _layout_toasts(self) -> None:
        """Пересчитывает позиции всех активных тостов."""
        if not self.main_window:
            return
            
        margin_bottom = 24
        margin_right = 24
        current_y = self.main_window.height() - margin_bottom
        
        # Toasts stack upwards
        for toast in reversed(self.active_toasts):
            current_y -= toast.height()
            x = self.main_window.width() - toast.width() - margin_right
            
            # Анимируем перемещение, если это не только что созданный тост
            if toast.y() != 0:
                anim = QPropertyAnimation(toast, b"pos", toast)
                anim.setDuration(200)
                anim.setStartValue(toast.pos())
                anim.setEndValue(QPoint(x, current_y))
                anim.setEasingCurve(QEasingCurve.Type.OutQuad)
                anim.start()
                # сохраняем ссылку чтобы GC не удалил анимацию
                toast._pos_anim = anim 
            else:
                toast.move(x, current_y)
                
            current_y -= 12  # Отступ между тостами

    def _on_toast_destroyed(self, toast: Toast) -> None:
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
            self._layout_toasts()
