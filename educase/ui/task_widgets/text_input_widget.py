# ui/task_widgets/text_input_widget.py
"""Виджет задания «Ввод текста» для студента."""
from PySide6.QtWidgets import QVBoxLayout, QLineEdit, QLabel
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from .base_task_widget import BaseTaskWidget


class TextInputWidget(BaseTaskWidget):
    def _setup_answer_ui(self, layout: QVBoxLayout):
        lbl = QLabel("Введите ваш ответ:")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(lbl)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ваш ответ...")
        self.input.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {COLORS['stroke_control']};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 16px;
                background: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
            }}
        """)
        self.input.textChanged.connect(lambda: self.answer_changed.emit())
        layout.addWidget(self.input)

    def get_answer(self) -> dict:
        return {"text": self.input.text()}

    def set_answer(self, data: dict):
        self.input.setText(data.get("text", ""))

    def set_readonly(self, readonly: bool):
        super().set_readonly(readonly)
        self.input.setReadOnly(readonly)
