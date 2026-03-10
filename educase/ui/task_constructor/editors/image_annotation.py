import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QFrame)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPixmap, QPen, QColor, QPainter

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon
from ..base_editor import AbstractTaskEditor

class InteractiveGraphicsView(QGraphicsView):
    """
    Кастомный View, позволяющий рисовать прямоугольники мышью.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.drawing = False
        self.start_point = QPointF()
        self.current_rect = None
        self.zones = []  # Список QGraphicsRectItem
        self.editor_parent = None
        self._pixmap = None

    def set_image(self, pixmap: QPixmap):
        self.scene().clear()
        self.zones.clear()
        self._pixmap = pixmap
        self.scene().addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))
        # Масштабируем изображение чтобы оно целиком помещалось в виджет
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._pixmap:
            self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
    def add_zone(self, rect: QRectF):
        pen = QPen(QColor(COLORS['accent']))
        pen.setWidth(2)
        brush = QColor(COLORS['accent'])
        brush.setAlpha(50)
        
        item = self.scene().addRect(rect, pen, brush)
        self.zones.append(item)
        if self.editor_parent:
            self.editor_parent.zones_changed()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            pos = self.mapToScene(event.pos())
            self.start_point = pos
            
            pen = QPen(QColor(COLORS['accent']))
            pen.setWidth(2)
            pen.setStyle(Qt.PenStyle.DashLine)
            self.current_rect = self.scene().addRect(QRectF(pos, pos), pen)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing and self.current_rect:
            pos = self.mapToScene(event.pos())
            rect = QRectF(self.start_point, pos).normalized()
            self.current_rect.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.drawing = False
            if self.current_rect:
                rect = self.current_rect.rect()
                self.scene().removeItem(self.current_rect)
                self.current_rect = None
                
                # Игнорируем слишком мелкие зоны (случайный клик)
                if rect.width() > 10 and rect.height() > 10:
                    self.add_zone(rect)
        super().mouseReleaseEvent(event)

    def clear_zones(self):
        for z in self.zones:
            self.scene().removeItem(z)
        self.zones.clear()
        if self.editor_parent:
            self.editor_parent.zones_changed()

class ImageAnnotationEditor(AbstractTaskEditor):
    """
    Редактор для задания типа "Зоны на изображении" (image_annotation).
    Позволяет загрузить картинку и нарисовать поверх нее правильные зоны ответа.
    """
    def __init__(self, parent=None):
        self.image_path = ""
        super().__init__(parent)
        
    def _setup_specific_ui(self, layout: QVBoxLayout):
        self.options_group = QWidget()
        self.options_layout = QVBoxLayout(self.options_group)
        self.options_layout.setContentsMargins(0, 16, 0, 0)
        self.options_layout.setSpacing(8)
        
        top_row = QHBoxLayout()
        title = QLabel("Изображение для анализа")
        title.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']};")
        
        self.btn_load = QPushButton("Загрузить изображение")
        self.btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg_layer']};
                color: {COLORS['accent']};
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{ background: {COLORS['state_hover']}; border-color: {COLORS['accent']}; }}
        """)
        self.btn_load.clicked.connect(self._load_image)
        
        self.btn_clear = QPushButton("Очистить зоны")
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.setStyleSheet(self.btn_load.styleSheet())
        self.btn_clear.clicked.connect(self._clear_zones)
        
        top_row.addWidget(title)
        top_row.addStretch()
        top_row.addWidget(self.btn_load)
        top_row.addWidget(self.btn_clear)
        self.options_layout.addLayout(top_row)
        
        self.view = InteractiveGraphicsView(self)
        self.view.editor_parent = self
        self.view.setMinimumHeight(300)
        self.view.setStyleSheet(f"background: {COLORS['bg_layer']}; border: 1px dashed {COLORS['stroke_control']};")
        self.options_layout.addWidget(self.view)
        
        self.lbl_info = QLabel("Зон выделено: 0 (Изображение не загружено)")
        self.lbl_info.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.options_layout.addWidget(self.lbl_info)
        
        layout.addWidget(self.options_group)

    def _load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(file_name)
            self.view.set_image(pixmap)
            self.lbl_info.setText("Картинка загружена. Нарисуйте прямоугольные зоны.")
            self.data_changed.emit()

    def _clear_zones(self):
        self.view.clear_zones()

    def zones_changed(self):
        count = len(self.view.zones)
        self.lbl_info.setText(f"Зон выделено: {count}")
        self.data_changed.emit()

    def get_specific_data(self) -> dict:
        zones_data = []
        for z in self.view.zones:
            r = z.rect()
            zones_data.append({
                "x": r.x(), "y": r.y(), 
                "width": r.width(), "height": r.height()
            })
            
        return {
            "image_path": self.image_path,
            "zones": zones_data
        }

    def set_specific_data(self, data: dict):
        self.image_path = data.get("image_path", "")
        if self.image_path:
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                self.view.set_image(pixmap)
                
                # Восстанавливаем зоны
                for z_dict in data.get("zones", []):
                    r = QRectF(z_dict["x"], z_dict["y"], z_dict["width"], z_dict["height"])
                    self.view.add_zone(r)
                
                self.zones_changed()
