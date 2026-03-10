# ui/task_widgets/image_annotation_widget.py
"""Виджет задания «Зоны на изображении» — клик/выделение зон на картинке."""
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QPushButton, QHBoxLayout
)
from typing import Optional
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPixmap, QPen, QColor, QBrush, QMouseEvent

from ui.styles.theme import COLORS
from .base_task_widget import BaseTaskWidget


class DrawingGraphicsView(QGraphicsView):
    """Кастомный QGraphicsView для рисования прямоугольных зон."""
    zone_drawn = Signal(dict)

    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.setMouseTracking(True)
        self._is_drawing = False
        self._start_pos = QPointF()
        self._current_rect_item: Optional[QGraphicsRectItem] = None
        self._readonly = False
        self.setCursor(Qt.CursorShape.CrossCursor)

    def set_readonly(self, readonly: bool):
        self._readonly = readonly
        self.setCursor(Qt.CursorShape.ArrowCursor if readonly else Qt.CursorShape.CrossCursor)

    def mousePressEvent(self, event: QMouseEvent):
        if self._readonly or event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        self._is_drawing = True
        self._start_pos = self.mapToScene(event.pos())
        self._current_rect_item = QGraphicsRectItem(QRectF(self._start_pos, self._start_pos))
        pen = QPen(QColor(COLORS["accent"]), 2)
        self._current_rect_item.setPen(pen)
        self._current_rect_item.setBrush(QBrush(QColor(COLORS["accent"] + "30")))
        self.scene().addItem(self._current_rect_item)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_drawing and self._current_rect_item:
            current_pos = self.mapToScene(event.pos())
            rect = QRectF(self._start_pos, current_pos).normalized()
            self._current_rect_item.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_drawing and event.button() == Qt.MouseButton.LeftButton:
            self._is_drawing = False
            if self._current_rect_item:
                rect = self._current_rect_item.rect()
                if rect.width() > 5 and rect.height() > 5:
                    zone_dict = {
                        "x": rect.x(),
                        "y": rect.y(),
                        "w": rect.width(),
                        "h": rect.height()
                    }
                    self.zone_drawn.emit(zone_dict)
                else:
                    self.scene().removeItem(self._current_rect_item)
                self._current_rect_item = None
        super().mouseReleaseEvent(event)


class ImageAnnotationWidget(BaseTaskWidget):
    def _setup_answer_ui(self, layout: QVBoxLayout):
        lbl = QLabel("Выделите нужные области на изображении:")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(lbl)

        self.gs = QGraphicsScene()
        self.gv = DrawingGraphicsView(self.gs)
        self.gv.setMinimumHeight(300)
        self.gv.setStyleSheet(f"""
            QGraphicsView {{
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: 8px;
                background: {COLORS['bg_elevated']};
            }}
        """)
        self.gv.setRenderHint(self.gv.renderHints())
        self.gv.zone_drawn.connect(self._on_zone_drawn)
        layout.addWidget(self.gv)

        self.zones: list[dict] = []

        # Кнопка очистки
        row = QHBoxLayout()
        row.addStretch()
        btn_clear = QPushButton("Очистить зоны")
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 4px; padding: 4px 12px;
            }}
            QPushButton:hover {{ background: {COLORS['state_hover']}; }}
        """)
        btn_clear.clicked.connect(self._clear_zones)
        row.addWidget(btn_clear)
        layout.addLayout(row)

    def _on_zone_drawn(self, zone: dict):
        self.zones.append(zone)
        self.answer_changed.emit()

    def set_task(self, task_data: dict):
        super().set_task(task_data)
        self.gs.clear()
        self.zones.clear()

        config = task_data.get("configuration", {})
        image_path = config.get("image_path", "")

        if image_path:
            pm = QPixmap(image_path)
            if not pm.isNull():
                self.gs.addPixmap(pm)
                self.gs.setSceneRect(QRectF(pm.rect()))
                self.gv.fitInView(self.gs.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def get_answer(self) -> dict:
        return {"zones": self.zones}

    def set_answer(self, data: dict):
        self.zones = data.get("zones", [])
        self._draw_zones()

    def _draw_zones(self):
        # Очистить старые отрисованные зоны (не картинку)
        for item in self.gs.items():
            if isinstance(item, QGraphicsRectItem):
                self.gs.removeItem(item)

        for z in self.zones:
            rect = QGraphicsRectItem(z["x"], z["y"], z["w"], z["h"])
            pen = QPen(QColor(COLORS["accent"]), 2)
            rect.setPen(pen)
            rect.setBrush(QBrush(QColor(COLORS["accent"] + "30")))
            self.gs.addItem(rect)

    def _clear_zones(self):
        # Удаляем только rect items, оставляем pixmap
        for item in self.gs.items():
            if isinstance(item, QGraphicsRectItem):
                self.gs.removeItem(item)
        self.zones.clear()
        self.answer_changed.emit()

    def set_readonly(self, readonly: bool):
        super().set_readonly(readonly)
        self.gv.set_readonly(readonly)

