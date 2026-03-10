# ui/task_widgets/timeline_widget.py
"""Виджет задания «Таймлайн» — упорядочивание событий (использует общий базовый класс)."""
from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import Qt

from .common_drag_list import DragListWidget


class TimelineWidget(DragListWidget):

    def _get_instruction_text(self) -> str:
        return "Расположите события в хронологическом порядке:"

    def _populate_list(self, task_data: dict):
        config = task_data.get("configuration", {})
        events = config.get("events", [])

        for ev in events:
            li = QListWidgetItem(f"📅  {ev.get('text', '')}")
            li.setData(Qt.ItemDataRole.UserRole, ev.get("id"))
            li.setFlags(li.flags() | Qt.ItemFlag.ItemIsDragEnabled)
            self.drag_list.addItem(li)

