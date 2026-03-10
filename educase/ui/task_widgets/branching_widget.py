# ui/task_widgets/branching_widget.py
"""Виджет задания «Ветвление» — карточки-кнопки выбора действия."""
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from .base_task_widget import BaseTaskWidget


class BranchingWidget(BaseTaskWidget):
    def _setup_answer_ui(self, layout: QVBoxLayout):
        lbl = QLabel("Выберите действие:")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(lbl)

        self.choice_buttons: list[dict] = []
        self.choices_layout = QVBoxLayout()
        self.choices_layout.setSpacing(10)
        layout.addLayout(self.choices_layout)
        self._selected_edge = None

    def set_task(self, task_data: dict):
        super().set_task(task_data)
        for cb in self.choice_buttons:
            cb["widget"].deleteLater()
        self.choice_buttons.clear()
        self._selected_edge = None

        config = task_data.get("configuration", {})
        edges = config.get("edges", [])

        for edge in edges:
            btn = QPushButton(edge.get("label", "Вариант"))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(60)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS['bg_elevated']};
                    border: 2px solid {COLORS['stroke_divider']};
                    border-radius: 10px;
                    color: {COLORS['text_primary']};
                    font-size: 15px;
                    font-weight: bold;
                    padding: 16px 24px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    border-color: {COLORS['accent']};
                    background: {COLORS['accent']}10;
                }}
            """)
            edge_id = edge.get("id")
            btn.clicked.connect(lambda checked, eid=edge_id: self._select_edge(eid))

            self.choices_layout.addWidget(btn)
            self.choice_buttons.append({"id": edge_id, "btn": btn, "widget": btn})

    def _select_edge(self, edge_id):
        self._selected_edge = edge_id
        # Подсвечиваем выбранную
        for cb in self.choice_buttons:
            if str(cb["id"]) == str(edge_id):
                cb["btn"].setStyleSheet(f"""
                    QPushButton {{
                        background: {COLORS['accent']}15;
                        border: 2px solid {COLORS['accent']};
                        border-radius: 10px;
                        color: {COLORS['accent']};
                        font-size: 15px;
                        font-weight: bold;
                        padding: 16px 24px;
                        text-align: left;
                    }}
                """)
            else:
                cb["btn"].setStyleSheet(f"""
                    QPushButton {{
                        background: {COLORS['bg_elevated']};
                        border: 2px solid {COLORS['stroke_divider']};
                        border-radius: 10px;
                        color: {COLORS['text_primary']};
                        font-size: 15px;
                        font-weight: bold;
                        padding: 16px 24px;
                        text-align: left;
                    }}
                    QPushButton:hover {{
                        border-color: {COLORS['accent']};
                        background: {COLORS['accent']}10;
                    }}
                """)
        self.answer_changed.emit()

    def get_answer(self) -> dict:
        if self._selected_edge is not None:
            return {"selected_edge_id": self._selected_edge}
        return {}

    def set_answer(self, data: dict):
        edge_id = data.get("selected_edge_id")
        if edge_id is not None:
            self._select_edge(edge_id)

    def set_readonly(self, readonly: bool):
        super().set_readonly(readonly)
        for cb in self.choice_buttons:
            cb["btn"].setEnabled(not readonly)
