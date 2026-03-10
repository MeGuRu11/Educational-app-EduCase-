# ui/task_widgets/single_choice_widget.py
"""Виджет задания «Один ответ» для студента."""
from PySide6.QtWidgets import (
    QVBoxLayout, QRadioButton, QButtonGroup, QWidget, QLabel
)
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from .base_task_widget import BaseTaskWidget


class SingleChoiceWidget(BaseTaskWidget):
    def _setup_answer_ui(self, layout: QVBoxLayout):
        self.radio_group = QButtonGroup(self)
        self.option_widgets: list[dict] = []
        self.options_layout = QVBoxLayout()
        self.options_layout.setSpacing(8)
        layout.addLayout(self.options_layout)

    def set_task(self, task_data: dict):
        super().set_task(task_data)

        # Очищаем
        for ow in self.option_widgets:
            self.radio_group.removeButton(ow["radio"])
            ow["widget"].deleteLater()
        self.option_widgets.clear()

        config = task_data.get("configuration", {})
        options = config.get("options", [])

        for opt in options:
            w = QWidget()
            w.setStyleSheet(f"""
                QWidget {{
                    background: {COLORS['bg_elevated']};
                    border: 1px solid {COLORS['stroke_divider']};
                    border-radius: 8px;
                    padding: 4px;
                }}
                QWidget:hover {{
                    border-color: {COLORS['accent']};
                    background: {COLORS['state_hover']};
                }}
            """)
            w.setCursor(Qt.CursorShape.PointingHandCursor)

            radio = QRadioButton(opt.get("text", ""))
            radio.setStyleSheet(f"""
                QRadioButton {{
                    color: {COLORS['text_primary']};
                    font-size: 14px;
                    padding: 10px 12px;
                    spacing: 10px;
                }}
            """)
            radio.toggled.connect(lambda: self.answer_changed.emit())

            inner = QVBoxLayout(w)
            inner.setContentsMargins(0, 0, 0, 0)
            inner.addWidget(radio)

            self.radio_group.addButton(radio)
            self.options_layout.addWidget(w)
            self.option_widgets.append({
                "id": opt.get("id"),
                "radio": radio,
                "widget": w,
            })

    def get_answer(self) -> dict:
        for ow in self.option_widgets:
            if ow["radio"].isChecked():
                return {"selected_option_id": ow["id"]}
        return {}

    def set_answer(self, data: dict):
        sel = data.get("selected_option_id")
        if sel is not None:
            for ow in self.option_widgets:
                if str(ow["id"]) == str(sel):
                    ow["radio"].setChecked(True)
                    break

    def set_readonly(self, readonly: bool):
        super().set_readonly(readonly)
        for ow in self.option_widgets:
            ow["radio"].setEnabled(not readonly)
