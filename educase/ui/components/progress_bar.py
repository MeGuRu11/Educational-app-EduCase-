# ui/components/progress_bar.py
from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QWidget

from ui.styles.theme import ANIM, COLORS


class ProgressBar(QWidget):
    """
    Линейный прогресс-бар с анимацией заполнения и закругленными краями.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0.0 # 0.0 to 1.0
        self._animated_value = 0.0
        self.setFixedHeight(8)

        self.anim = QPropertyAnimation(self, b"animated_value", self)
        self.anim.setDuration(ANIM["medium"])
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def get_animated_value(self) -> float:
        return self._animated_value

    def set_animated_value(self, val: float):
        self._animated_value = val
        self.update()

    animated_value = Property(float, get_animated_value, set_animated_value)

    def set_value(self, value: float, animated: bool = True):
        # clamp between 0 and 1
        value = max(0.0, min(1.0, value))
        self._value = value

        if animated:
            self.anim.stop()
            self.anim.setStartValue(self._animated_value)
            self.anim.setEndValue(self._value)
            self.anim.start()
        else:
            self.set_animated_value(self._value)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        bg_path = QPainterPath()
        bg_path.addRoundedRect(self.rect(), self.height()/2, self.height()/2)
        p.fillPath(bg_path, QColor(0, 0, 0, 20)) # stroke_card

        # Fill
        if self._animated_value > 0:
            fill_width = self.width() * self._animated_value
            fill_rect = self.rect()
            fill_rect.setWidth(fill_width)

            fill_path = QPainterPath()
            fill_path.addRoundedRect(fill_rect, self.height()/2, self.height()/2)

            # Change color based on completion
            if self._animated_value >= 1.0:
                color = QColor(COLORS["success"])
            else:
                color = QColor(COLORS["accent"])

            p.fillPath(fill_path, color)
