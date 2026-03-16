# ui/components/heatmap_widget.py
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QToolTip, QLabel

from ui.styles.dashboard_theme import FONT


class HeatmapWidget(QLabel):
    """
    Сложный кастомный виджет для отрисовки тепловой карты выполнения заданий.
    Использует QPixmap для стабильности (избежание конфликтов QPainter).
    """
    def __init__(self, students: list[str], task_count: int,
                 data: list[list[float]], parent=None):
        super().__init__(parent)
        self.students = students
        self.task_count = task_count
        self.data = data

        # Размеры ячейки
        self.CELL_W = 22
        self.CELL_H = 16
        self.CELL_GAP = 3
        self.LABEL_WIDTH = 90

        self.setMouseTracking(True)
        self._hover_idx = (-1, -1)

        # Рассчитаем фиксированный размер
        w = self.LABEL_WIDTH + (self.CELL_W + self.CELL_GAP) * task_count + 20
        h = 30 + (self.CELL_H + self.CELL_GAP) * len(students) + 60
        self.setFixedSize(w, h)
        self._render_pixmap()

    def _get_color_for_value(self, t: float) -> QColor:
        t = max(0.0, min(1.0, t))
        if t < 0.5:
            factor = t * 2.0
            r = int(196 + (245 - 196) * factor)
            g = int(43 + (158 - 43) * factor)
            b = int(28 + (11 - 28) * factor)
        else:
            factor = (t - 0.5) * 2.0
            r = int(245 + (16 - 245) * factor)
            g = int(158 + (124 - 158) * factor)
            b = int(11 + (16 - 11) * factor)
        return QColor(r, g, b)

    def _render_pixmap(self):
        pix = QPixmap(self.size())
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Смещения
        base_x = self.LABEL_WIDTH
        base_y = 25

        # 1. Заголовки колонок (задания)
        p.setPen(QColor("#9BA3B4"))
        p.setFont(QFont(FONT, 9))
        for j in range(self.task_count):
            x = base_x + j * (self.CELL_W + self.CELL_GAP)
            r = QRectF(x, 0, self.CELL_W, 20)
            p.drawText(r, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom, str(j+1))

        # 2. Строки учеников
        for i, student in enumerate(self.students):
            y = base_y + i * (self.CELL_H + self.CELL_GAP)

            # Имя
            p.setPen(QColor("#5A6478"))
            p.setFont(QFont(FONT, 10, QFont.Weight.DemiBold))
            name_rect = QRectF(0, y, self.LABEL_WIDTH - 10, self.CELL_H)

            # Эмуляция text-overflow ellipsis вручную
            fm = p.fontMetrics()
            elided_name = fm.elidedText(student, Qt.TextElideMode.ElideRight, int(name_rect.width()))
            p.drawText(name_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, elided_name)

            # Ячейки
            p.setPen(Qt.PenStyle.NoPen)
            if i < len(self.data):
                row_data = self.data[i]
                for j in range(min(self.task_count, len(row_data))):
                    val = row_data[j]
                    x = base_x + j * (self.CELL_W + self.CELL_GAP)

                    color = self._get_color_for_value(val)
                    p.setBrush(QBrush(color))
                    p.drawRoundedRect(QRectF(x, y, self.CELL_W, self.CELL_H), 3, 3)

                    # Highlight on hover
                    if (i, j) == self._hover_idx:
                        p.setBrush(Qt.BrushStyle.NoBrush)
                        p.setPen(QPen(QColor(0,0,0, 100), 2))
                        p.drawRoundedRect(QRectF(x, y, self.CELL_W, self.CELL_H), 3, 3)
                        p.setPen(Qt.PenStyle.NoPen)

        # 3. Легенда (градиент)
        leg_y = base_y + len(self.students) * (self.CELL_H + self.CELL_GAP) + 20
        leg_w = 150
        leg_x = base_x
        leg_h = 6

        grad = QLinearGradient(leg_x, 0, leg_x + leg_w, 0)
        grad.setColorAt(0.0, QColor(196, 43, 28))   # red
        grad.setColorAt(0.5, QColor(245, 158, 11))  # amber
        grad.setColorAt(1.0, QColor(16, 124, 16))   # green

        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRectF(leg_x, leg_y, leg_w, leg_h), 3, 3)

        p.setPen(QColor("#9BA3B4"))
        p.setFont(QFont(FONT, 10))
        p.drawText(QRectF(leg_x - 30, leg_y - 8, 25, 20), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "0%")
        p.drawText(QRectF(leg_x + leg_w + 5, leg_y - 8, 35, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "100%")
        p.end()
        self.setPixmap(pix)

    def mouseMoveEvent(self, event):
        pos = event.position()
        base_x = self.LABEL_WIDTH
        base_y = 25

        j = int((pos.x() - base_x) // (self.CELL_W + self.CELL_GAP))
        i = int((pos.y() - base_y) // (self.CELL_H + self.CELL_GAP))

        in_cell_x = base_x + j * (self.CELL_W + self.CELL_GAP) <= pos.x() <= base_x + j * (self.CELL_W + self.CELL_GAP) + self.CELL_W
        in_cell_y = base_y + i * (self.CELL_H + self.CELL_GAP) <= pos.y() <= base_y + i * (self.CELL_H + self.CELL_GAP) + self.CELL_H

        if 0 <= i < len(self.students) and 0 <= j < self.task_count and in_cell_x and in_cell_y:
            if self._hover_idx != (i, j):
                self._hover_idx = (i, j)
                self._render_pixmap()
                val = self.data[i][j]
                QToolTip.showText(event.globalPos(), f"{self.students[i]} · Задание {j+1} · {int(val*100)}%", self)
        else:
            if self._hover_idx != (-1, -1):
                self._hover_idx = (-1, -1)
                self._render_pixmap()
                QToolTip.hideText()
