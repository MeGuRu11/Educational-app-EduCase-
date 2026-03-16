# ui/components/stepper.py
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from ui.styles.theme import COLORS


class Stepper(QWidget):
    """
    Визуализирует шаги процесса: (1) --- (2) --- (3)
    """
    def __init__(self, steps: list[str], current_step: int = 0, parent=None):
        super().__init__(parent)
        self.steps = steps
        self.current_step = current_step
        self.setFixedHeight(60)

    def set_step(self, step_idx: int):
        self.current_step = max(0, min(len(self.steps) - 1, step_idx))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        num_steps = len(self.steps)
        if num_steps <= 1:
            return

        w = self.width()
        h = self.height()
        radius = 12
        margin = 30

        available_w = w - (margin * 2)
        spacing = available_w / (num_steps - 1)

        # 1. Draw connecting lines
        y_center = h / 2 - 10

        for i in range(num_steps - 1):
            x1 = margin + (i * spacing)
            x2 = margin + ((i + 1) * spacing)

            # Line color based on completion
            if i < self.current_step:
                p.setPen(QPen(QColor(COLORS["accent"]), 3))
            else:
                p.setPen(QPen(QColor(0, 0, 0, 20), 3)) # stroke_card

            p.drawLine(x1, y_center, x2, y_center)

        # 2. Draw nodes and text
        font = QFont("Segoe UI Variable", 10)
        font.setBold(True)
        p.setFont(font)

        text_font = QFont("Segoe UI Variable", 8)

        for i, text in enumerate(self.steps):
            x = margin + (i * spacing)

            # Draw circle
            path = QPainterPath()
            path.addEllipse(x - radius, y_center - radius, radius * 2, radius * 2)

            if i < self.current_step:
                # Completed
                p.fillPath(path, QColor(COLORS["accent"]))
                p.setPen(Qt.PenStyle.NoPen)
                # white checkmark or number
                p.setPen(QColor("white"))
                p.drawText(int(x - radius), int(y_center - radius), radius * 2, radius * 2, Qt.AlignmentFlag.AlignCenter, str(i + 1))
            elif i == self.current_step:
                # Current
                p.fillPath(path, QColor(COLORS["bg_elevated"]))
                p.setPen(QPen(QColor(COLORS["accent"]), 3))
                p.drawPath(path)
                p.setPen(QColor(COLORS["accent"]))
                p.drawText(int(x - radius), int(y_center - radius), radius * 2, radius * 2, Qt.AlignmentFlag.AlignCenter, str(i + 1))
            else:
                # Future
                p.fillPath(path, QColor(COLORS["bg_elevated"]))
                p.setPen(QPen(QColor(0, 0, 0, 20), 2)) # stroke_card
                p.drawPath(path)
                p.setPen(QColor(COLORS["text_secondary"]))
                p.drawText(int(x - radius), int(y_center - radius), radius * 2, radius * 2, Qt.AlignmentFlag.AlignCenter, str(i + 1))

            # Draw label under circle
            p.setFont(text_font)
            if i <= self.current_step:
                p.setPen(QColor(COLORS["text_primary"]))
            else:
                p.setPen(QColor(COLORS["text_secondary"]))

            # rect for text underneath
            text_rect = p.boundingRect(int(x - 50), int(y_center + radius + 5), 100, 20, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, text)
            p.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, text)
            p.setFont(font) # reset to bold font
