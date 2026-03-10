from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QFrame, QScrollArea)
from PySide6.QtCore import Qt, QMimeData, QPoint
from PySide6.QtGui import QDrag, QPixmap

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon
from ..base_editor import AbstractTaskEditor

class DraggableItem(QFrame):
    def __init__(self, item_id, editor_parent, drag_callback):
        super().__init__()
        self.item_id = item_id
        self.editor = editor_parent
        self.drag_callback = drag_callback

        self.setStyleSheet(f"background: {COLORS['bg_elevated']}; border: 1px solid {COLORS['stroke_divider']}; border-radius: 6px;")
        
        self.setAcceptDrops(True)
        self.drag_start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Разрешаем перетаскивание только если курсор находится над иконкой "drag_handle" (самая левая)
            drag_lbl = self.findChild(QLabel)
            if drag_lbl and drag_lbl.geometry().contains(event.pos()):
                self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or not self.drag_start_pos:
            return
            
        distance = (event.pos() - self.drag_start_pos).manhattanLength()
        if distance < 10:  # Защита от случайного сдвига
            return
            
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.item_id)
        drag.setMimeData(mime_data)
        
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        
        drag.exec(Qt.DropAction.MoveAction)
        self.drag_start_pos = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            source_id = event.mimeData().text()
            if source_id != self.item_id:
                event.accept()
                self.setStyleSheet(f"background: {COLORS['bg_layer']}; border: 2px dashed {COLORS['accent']}; border-radius: 6px;")
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(f"background: {COLORS['bg_elevated']}; border: 1px solid {COLORS['stroke_divider']}; border-radius: 6px;")
        
    def dropEvent(self, event):
        self.setStyleSheet(f"background: {COLORS['bg_elevated']}; border: 1px solid {COLORS['stroke_divider']}; border-radius: 6px;")
        if event.mimeData().hasText():
            source_id = event.mimeData().text()
            self.drag_callback(source_id, self.item_id)
            event.accept()

class OrderingEditor(AbstractTaskEditor):
    """
    Редактор для задания типа "Сортировка" (ordering).
    Позволяет добавлять элементы списка в правильном порядке.
    """
    def __init__(self, parent=None):
        self.options = [] # Список dict: {"id": str, "widget": QWidget, "input": QLineEdit}
        self.option_counter = 0
        super().__init__(parent)
        
    def _setup_specific_ui(self, layout: QVBoxLayout):
        self.options_group = QWidget()
        self.options_layout = QVBoxLayout(self.options_group)
        self.options_layout.setContentsMargins(0, 16, 0, 0)
        self.options_layout.setSpacing(8)
        
        title = QLabel("Элементы (в правильном порядке)")
        title.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']};")
        self.options_layout.addWidget(title)
        
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.options_layout.addWidget(self.list_container)
        
        self.btn_add = QPushButton("+ Добавить элемент")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['accent']};
                font-weight: bold;
                border: 2px dashed {COLORS['accent']}40;
                border-radius: 6px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background: {COLORS['state_hover']};
                border-color: {COLORS['accent']};
            }}
        """)
        self.btn_add.clicked.connect(self._add_empty_option)
        self.options_layout.addWidget(self.btn_add)
        
        # Вставляем готовый блок в переданный layout
        layout.addWidget(self.options_group)
        
        # Добавим три дефолтных варианта по умолчанию для наглядности
        self._add_empty_option()
        self._add_empty_option()
        self._add_empty_option()

    def _add_empty_option(self):
        opt_id = f"opt_{self.option_counter}"
        self.option_counter += 1
        
        row = DraggableItem(opt_id, self, self._handle_drop)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(12, 8, 12, 8)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        lbl_drag = QLabel()
        lbl_drag.setPixmap(get_icon("drag_handle", COLORS["text_secondary"], 20).pixmap(20, 20))
        lbl_drag.setFixedSize(24, 24)
        lbl_drag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_drag.setStyleSheet("border: none; background: transparent;")
        
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(f"Элемент {len(self.options) + 1}")
        line_edit.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
            QLineEdit:focus {{ outline: none; }}
        """)
        line_edit.textChanged.connect(lambda: self.data_changed.emit())
        
        btn_del = QPushButton()
        btn_del.setIcon(get_icon("delete", COLORS["error"], 18))
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet("border: none; background: transparent; padding: 4px; margin: 0;")
        btn_del.clicked.connect(lambda: self._remove_option(opt_id))
        
        row_layout.addWidget(lbl_drag, alignment=Qt.AlignmentFlag.AlignVCenter)
        row_layout.addWidget(line_edit, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)
        row_layout.addWidget(btn_del, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        self.list_layout.addWidget(row)
        
        self.options.append({
            "id": opt_id,
            "widget": row,
            "input": line_edit
        })
        
        self._update_placeholders()
        self.data_changed.emit()

    def _handle_drop(self, source_id: str, target_id: str):
        # Находим индексы
        source_idx = next(i for i, opt in enumerate(self.options) if opt["id"] == source_id)
        target_idx = next(i for i, opt in enumerate(self.options) if opt["id"] == target_id)
        
        if source_idx == target_idx:
            return
            
        # Убираем исходный элемент из списка и layout
        item = self.options.pop(source_idx)
        self.list_layout.removeWidget(item["widget"])
        
        # Вставляем на новое место
        self.options.insert(target_idx, item)
        self.list_layout.insertWidget(target_idx, item["widget"])
        
        self._update_placeholders()
        self.data_changed.emit()

    def _remove_option(self, opt_id: str):
        if len(self.options) <= 2:
            return  # Для сортировки нужно минимум 2 элемента
            
        target_opt = next((o for o in self.options if o["id"] == opt_id), None)
        if target_opt:
            self.list_layout.removeWidget(target_opt["widget"])
            target_opt["widget"].deleteLater()
            self.options.remove(target_opt)
            
            self._update_placeholders()
            self.data_changed.emit()

    def _update_placeholders(self):
        for i, opt in enumerate(self.options):
            opt["input"].setPlaceholderText(f"Элемент {i + 1}")

    def get_specific_data(self) -> dict:
        items = []
        for i, opt in enumerate(self.options):
            text = opt["input"].text().strip()
            if text:
                items.append({
                    "id": opt["id"],
                    "text": text,
                    "order": i
                })
        return {"items": items}

    def set_specific_data(self, data: dict):
        for opt in list(self.options):
            self._remove_option(opt["id"])
            
        items = data.get("items", [])
        if not items:
            self._add_empty_option()
            self._add_empty_option()
            return
            
        # Сортируем по order на всякий случай
        items.sort(key=lambda x: x.get("order", 0))
        
        self.option_counter = 0
        self.options.clear()
        
        for item in items:
            self._add_empty_option()
            last_opt = self.options[-1]
            last_opt["input"].setText(item.get("text", ""))
