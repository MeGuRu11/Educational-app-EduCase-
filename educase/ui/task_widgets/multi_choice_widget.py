# ui/task_widgets/multi_choice_widget.py
"""Виджет задания «Несколько ответов» для студента."""
from PySide6.QtWidgets import QVBoxLayout, QCheckBox, QWidget
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from .base_task_widget import BaseTaskWidget


class MultiChoiceWidget(BaseTaskWidget):
    def _setup_answer_ui(self, layout: QVBoxLayout):
        self.option_widgets: list[dict] = []
        self.options_layout = QVBoxLayout()
        self.options_layout.setSpacing(8)
        layout.addLayout(self.options_layout)

    def set_task(self, task_data: dict):
        super().set_task(task_data)
        for ow in self.option_widgets:
            ow["widget"].deleteLater()
        self.option_widgets.clear()

        config = task_data.get("configuration", {})
        for opt in config.get("options", []):
            w = QWidget()
            w.setStyleSheet(f"""
                QWidget {{
                    background: {COLORS['bg_elevated']};
                    border: 1px solid {COLORS['stroke_divider']};
                    border-radius: 8px;
                }}
                QWidget:hover {{
                    border-color: {COLORS['accent']};
                    background: {COLORS['state_hover']};
                }}
            """)
            w.setCursor(Qt.CursorShape.PointingHandCursor)

            cb = QCheckBox(opt.get("text", ""))
            cb.setStyleSheet(f"""
                QCheckBox {{
                    color: {COLORS['text_primary']};
                    font-size: 14px;
                    padding: 10px 12px;
                    spacing: 10px;
                }}
            """)
            cb.toggled.connect(lambda: self.answer_changed.emit())

            inner = QVBoxLayout(w)
            inner.setContentsMargins(0, 0, 0, 0)
            inner.addWidget(cb)

            self.options_layout.addWidget(w)
            self.option_widgets.append({"id": opt.get("id"), "cb": cb, "widget": w})

    def get_answer(self) -> dict:
        selected = [ow["id"] for ow in self.option_widgets if ow["cb"].isChecked()]
        return {"selected_option_ids": selected}

    def set_answer(self, data: dict):
        ids = {str(s) for s in data.get("selected_option_ids", [])}
        for ow in self.option_widgets:
            ow["cb"].setChecked(str(ow["id"]) in ids)

    def set_readonly(self, readonly: bool):
        super().set_readonly(readonly)
        for ow in self.option_widgets:
            ow["cb"].setEnabled(not readonly)
