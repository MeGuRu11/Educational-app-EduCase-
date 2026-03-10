# ui/task_widgets/common_drag_list.py
"""Общий базовый класс для заданий с сортировкой элементов перетаскиванием."""
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QAbstractItemView
)
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from .base_task_widget import BaseTaskWidget


class DragListWidget(BaseTaskWidget):
    """
    Абстрактный виджет для сортировки/таймлайна.
    Субклассы реализуют `_populate_list(task_data)` для настройки элементов и текста.
    """
    
    def _get_instruction_text(self) -> str:
        return "Перетаскивайте элементы в правильном порядке:"
        
    def _setup_answer_ui(self, layout: QVBoxLayout):
        lbl = QLabel(self._get_instruction_text())
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(lbl)

        self.drag_list = QListWidget()
        self.drag_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.drag_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.drag_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: 8px;
                background: {COLORS['bg_elevated']};
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px 16px;
                border-bottom: 1px solid {COLORS['stroke_divider']};
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
            QListWidget::item:hover {{
                background: {COLORS['state_hover']};
            }}
            QListWidget::item:selected {{
                background: {COLORS['accent']}20;
                color: {COLORS['text_primary']};
            }}
        """)
        self.drag_list.setMinimumHeight(200)
        self.drag_list.model().rowsMoved.connect(lambda: self.answer_changed.emit())
        layout.addWidget(self.drag_list)

    def set_task(self, task_data: dict):
        super().set_task(task_data)
        self.drag_list.clear()
        self._populate_list(task_data)

    def _populate_list(self, task_data: dict):
        """Реализуется в субклассах для добавления элементов QListWidgetItem."""
        pass

    def get_answer(self) -> dict:
        order = []
        for i in range(self.drag_list.count()):
            item = self.drag_list.item(i)
            order.append(item.data(Qt.ItemDataRole.UserRole))
        return {"order": order}

    def set_answer(self, data: dict):
        saved_order = data.get("order", [])
        if not saved_order:
            return
            
        items_map = {}
        for i in range(self.drag_list.count()):
            item = self.drag_list.item(i)
            items_map[str(item.data(Qt.ItemDataRole.UserRole))] = item.text()

        self.drag_list.clear()
        for item_id in saved_order:
            text = items_map.get(str(item_id), "")
            if text:
                li = QListWidgetItem(text)
                li.setData(Qt.ItemDataRole.UserRole, item_id)
                li.setFlags(li.flags() | Qt.ItemFlag.ItemIsDragEnabled)
                self.drag_list.addItem(li)

    def set_readonly(self, readonly: bool):
        super().set_readonly(readonly)
        mode = QAbstractItemView.DragDropMode.NoDragDrop if readonly else QAbstractItemView.DragDropMode.InternalMove
        self.drag_list.setDragDropMode(mode)
