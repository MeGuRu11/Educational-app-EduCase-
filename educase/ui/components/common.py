# ui/components/common.py
"""
Общие компоненты UI для Dashboard-ов.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QWidget,
)

from ui.styles.dashboard_theme import COLORS, FONT, RADIUS


class CardFrame(QFrame):
    """Базовый контейнер-карточка (белый фон, скругления, тень)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CardFrame")
        self.setStyleSheet(f"""
            #CardFrame {{
                background-color: {COLORS["card"]};
                border-radius: {RADIUS["card"]}px;
                border: 1px solid {COLORS["border"]};
            }}
        """)

        # Легкая тень (соответствует shadow_md из макетов)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(6)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)


class SectionLabel(QWidget):
    """Заголовок секции (стиль: 13px, bold, primary color) с горизонтальной линией."""
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)

        label = QLabel(text)
        label.setStyleSheet(f"""
            color: {COLORS["t1"]};
            font-family: "{FONT}";
            font-size: 13px;
            font-weight: 800;
        """)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        line.setStyleSheet(f"color: {COLORS['border']};")

        layout.addWidget(label)
        layout.addWidget(line, 1)


class HoverCardFrame(CardFrame):
    """Карточка, которая приподнимается при наведении курсора (StatCard, GroupCard)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._base_y = 0
        self._is_ready = False

    def showEvent(self, event):
        super().showEvent(event)
        self._base_y = self.y()
        self._is_ready = True

    def enterEvent(self, event):
        super().enterEvent(event)
        if not self._is_ready:
            return

        from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation
        anim = QPropertyAnimation(self, b"pos", self)
        anim.setDuration(180)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setEndValue(QPoint(self.x(), self._base_y - 2))
        anim.start()
        # Сохраняем ссылку на анимацию
        self._anim = anim

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if not self._is_ready:
            return

        from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation
        anim = QPropertyAnimation(self, b"pos", self)
        anim.setDuration(180)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setEndValue(QPoint(self.x(), self._base_y))
        anim.start()
        self._anim = anim


class ScorePill(QLabel):
    """Цветной бейдж с процентом (для таблиц и ленты)."""
    def __init__(self, score: int, parent=None):
        super().__init__(f"{score}%", parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if score >= 75:
            bg, color = COLORS["success_bg"], "#0B5E0B"
        elif score >= 60:
            bg, color = COLORS["warning_bg"], "#7A4800"
        else:
            bg, color = COLORS["error_bg"], "#A01010"

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {color};
                padding: 4px 10px;
                border-radius: {RADIUS["pill"]}px;
                font-family: "{FONT}";
                font-size: 12px;
                font-weight: 700;
            }}
        """)


class GradeBadge(QLabel):
    """Круглый значок оценки (2/3/4/5)."""
    def __init__(self, grade: int, parent=None):
        super().__init__(str(grade), parent)
        self.setFixedSize(28, 28)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if grade == 5:
            bg, color = COLORS["success_bg"], "#0B5E0B"
        elif grade == 4:
            bg, color = "#EFF6FC", "#005A9E"
        elif grade == 3:
            bg, color = COLORS["warning_bg"], "#7A4800"
        else:
            bg, color = COLORS["error_bg"], "#C42B1C"

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {color};
                border-radius: 14px;
                font-family: "{FONT}";
                font-size: 13px;
                font-weight: 800;
            }}
        """)
