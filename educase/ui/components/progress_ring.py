# ui/components/progress_ring.py
from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.styles.theme import ANIM, COLORS


class ProgressRing(QWidget):
    """
    Круговой прогресс бар (кольцо).
    Используется для кейсов и статистики.
    """
    def __init__(self, size: int = 60, stroke_width: int = 6, show_text: bool = True, parent=None):
        super().__init__(parent)
        self._size = size
        self.stroke_width = stroke_width
        self.show_text = show_text

        self.setFixedSize(size, size)

        self._value = 0.0 # 0.0 to 1.0
        self._animated_value = 0.0

        self.anim = QPropertyAnimation(self, b"animated_value", self)
        self.anim.setDuration(ANIM["slow"])
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

        # Determine center and radius
        rect = QRectF(
            self.stroke_width / 2,
            self.stroke_width / 2,
            self._size - self.stroke_width,
            self._size - self.stroke_width
        )

        # Draw background ring
        bg_pen = QPen(QColor(0, 0, 0, 20), self.stroke_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(bg_pen)
        p.drawEllipse(rect)

        # Draw progress arc
        if self._animated_value > 0:
            if self._animated_value >= 1.0:
                fg_color = QColor(COLORS["success"])
            else:
                fg_color = QColor(COLORS["accent"])

            fg_pen = QPen(fg_color, self.stroke_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            p.setPen(fg_pen)

            # Angles in 1/16th of a degree
            start_angle = 90 * 16 # Start from top
            span_angle = int(-360 * self._animated_value * 16) # Negative is clockwise

            p.drawArc(rect, start_angle, span_angle)

        # Draw text
        if self.show_text:
            percentage = int(self._animated_value * 100)
            p.setPen(QColor(COLORS["text_primary"]))

            font = QFont("Segoe UI Variable", max(8, self._size // 5))
            font.setBold(True)
            p.setFont(font)

            # Draw text dead center
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{percentage}%")
