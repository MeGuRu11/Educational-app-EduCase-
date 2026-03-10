# ui/task_constructor/scenario_builder/graph_view.py
"""
QGraphicsView с поддержкой zoom (Ctrl+колёсико), pan (средняя кнопка),
и кнопкой «Уместить всё».
"""
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen

from ui.styles.theme import COLORS


class GraphView(QGraphicsView):
    """
    Виджет отображения графа с навигацией:
    - Zoom: Ctrl + колёсико мыши
    - Pan: правая кнопка мыши / Пробел + drag
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        # Минимальный / максимальный зум
        self._zoom = 1.0
        self._zoom_min = 0.2
        self._zoom_max = 3.0

        # Панарнинг
        self._panning = False
        self._pan_start = None

        self.setStyleSheet(f"""
            QGraphicsView {{
                background: {COLORS['bg_base']};
                border: none;
            }}
        """)

    def wheelEvent(self, event):
        """Zoom через Ctrl + колёсико."""
        factor = 1.15
        if event.angleDelta().y() > 0:
            # Zoom in
            if self._zoom < self._zoom_max:
                self.scale(factor, factor)
                self._zoom *= factor
        else:
            # Zoom out
            if self._zoom > self._zoom_min:
                self.scale(1 / factor, 1 / factor)
                self._zoom /= factor

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning and self._pan_start:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self._pan_start = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def fit_all(self):
        """Масштабирует вид, чтобы все элементы были видны."""
        rect = self.scene().itemsBoundingRect()
        if not rect.isNull():
            rect.adjust(-50, -50, 50, 50)
            self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom = self.transform().m11()

    def zoom_in(self):
        if self._zoom < self._zoom_max:
            self.scale(1.25, 1.25)
            self._zoom *= 1.25

    def zoom_out(self):
        if self._zoom > self._zoom_min:
            self.scale(0.8, 0.8)
            self._zoom *= 0.8

    def drawBackground(self, painter: QPainter, rect):
        """Рисуем сетку на фоне."""
        super().drawBackground(painter, rect)

        # Мелкая сетка
        grid_size = 25
        pen = QPen(QColor(COLORS["stroke_divider"]))
        pen.setWidthF(0.5)
        painter.setPen(pen)

        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        lines = []
        x = left
        while x < rect.right():
            lines.append((x, rect.top(), x, rect.bottom()))
            x += grid_size
        y = top
        while y < rect.bottom():
            lines.append((rect.left(), y, rect.right(), y))
            y += grid_size

        for x1, y1, x2, y2 in lines:
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
