# ui/components/loading_overlay.py
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.styles.theme import COLORS


class Spinner(QLabel):
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
        self._render_pixmap()

    def _rotate(self):
        self.angle = (self.angle + 6) % 360
        self._render_pixmap()

    def _render_pixmap(self):
        pix = QPixmap(self.size())
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = pix.rect().adjusted(4, 4, -4, -4)

        # Track
        p.setPen(QPen(QColor(0, 0, 0, 13), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(rect, 0, 360 * 16)

        # Arc
        p.setPen(QPen(QColor(COLORS["accent"]), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(rect, -self.angle * 16, 90 * 16)
        p.end()
        self.setPixmap(pix)


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

        # Используем полупрозрачный фон через stylesheet вместо paintEvent
        self.setStyleSheet(f"background-color: rgba(255, 255, 255, 180);")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        self.spinner = Spinner(48)

        self.text_lbl = QLabel(text)
        self.text_lbl.setStyleSheet(f"font-size: 16px; font-weight: 500; color: {COLORS['text_primary']};")

        layout.addWidget(self.spinner, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.text_lbl, 0, Qt.AlignmentFlag.AlignHCenter)


    def showEvent(self, event):
        if self.parent():
            self.resize(self.parent().size())
        super().showEvent(event)
