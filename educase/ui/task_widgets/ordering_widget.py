# ui/task_widgets/ordering_widget.py
"""Виджет задания «Сортировка» с drag&drop (использует общий базовый класс)."""
from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import Qt

from .common_drag_list import DragListWidget


class OrderingWidget(DragListWidget):
    
    def _get_instruction_text(self) -> str:
        return "Перетаскивайте элементы в правильном порядке:"

    def _populate_list(self, task_data: dict):
        config = task_data.get("configuration", {})
        items = config.get("items", [])

        for item in items:
            li = QListWidgetItem(f"☰  {item.get('text', '')}")
            li.setData(Qt.ItemDataRole.UserRole, item.get("id"))
            li.setFlags(li.flags() | Qt.ItemFlag.ItemIsDragEnabled)
            self.drag_list.addItem(li)

