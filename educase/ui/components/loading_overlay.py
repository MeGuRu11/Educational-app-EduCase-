# ui/components/loading_overlay.py
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.styles.theme import COLORS


class Spinner(QWidget):
    """
    Анимированный индикатор загрузки (вращающееся кольцо).
    """
    def __init__(self, size=40, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.angle = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)
        self.timer.start(16) # ~60 fps

    def _rotate(self):
        self.angle = (self.angle + 6) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(4, 4, -4, -4)

        # Draw background track
        p.setPen(QPen(QColor(0, 0, 0, 13), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)) # stroke_divider
        p.drawArc(rect, 0, 360 * 16)

        # Draw spinning arc
        p.setPen(QPen(QColor(COLORS["accent"]), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        # Start angle shifts, span angle stays constant (e.g. 1/4 of circle)
        p.drawArc(rect, -self.angle * 16, 90 * 16)


class LoadingOverlay(QWidget):
    """
    Оверлей на весь экран, блокирующий клики и показывающий спиннер.
    """
    def __init__(self, parent=None, text="Загрузка..."):
        super().__init__(parent)

        if parent:
            self.resize(parent.size())

        # Блокируем клики под оверлеем
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        self.spinner = Spinner(48)

        self.text_lbl = QLabel(text)
        self.text_lbl.setStyleSheet(f"font-size: 16px; font-weight: 500; color: {COLORS['text_primary']};")

        layout.addWidget(self.spinner, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.text_lbl, 0, Qt.AlignmentFlag.AlignHCenter)

    def paintEvent(self, event):
        p = QPainter(self)
        # Полупрозрачный белый (светлый) или темный фон в зависимости от темы
        # В нашем случае светлая с легким блюром/затемнением
        p.fillRect(self.rect(), QColor(255, 255, 255, 180))

    def showEvent(self, event):
        if self.parent():
            self.resize(self.parent().size())
        super().showEvent(event)
