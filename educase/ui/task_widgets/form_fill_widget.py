# ui/task_widgets/form_fill_widget.py
"""Виджет задания «Заполнение формы» — текст с инлайн-полями."""
from PySide6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QWidget
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from .base_task_widget import BaseTaskWidget


class FormFillWidget(BaseTaskWidget):
    def _setup_answer_ui(self, layout: QVBoxLayout):
        self.token_inputs: dict[str, QLineEdit] = {}
        self.tokens_layout = QVBoxLayout()
        self.tokens_layout.setSpacing(8)
        layout.addLayout(self.tokens_layout)

    def set_task(self, task_data: dict):
        super().set_task(task_data)
        # Очищаем
        for w in list(self.token_inputs.values()):
            w.parent().deleteLater() if w.parent() else w.deleteLater()
        self.token_inputs.clear()

        config = task_data.get("configuration", {})
        answers = config.get("answers", {})

        for token in sorted(answers.keys()):
            row = QWidget()
            row.setStyleSheet(f"""
                QWidget {{
                    background: {COLORS['bg_elevated']};
                    border: 1px solid {COLORS['stroke_divider']};
                    border-radius: 6px;
                }}
            """)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 8, 12, 8)

            lbl = QLabel(f"[{token}]")
            lbl.setStyleSheet(f"font-weight: bold; color: {COLORS['accent']}; border: none;")
            lbl.setFixedWidth(60)

            inp = QLineEdit()
            inp.setPlaceholderText(f"Ответ для [{token}]...")
            inp.setStyleSheet(f"""
                QLineEdit {{
                    border: none; background: transparent;
                    color: {COLORS['text_primary']}; font-size: 14px;
                }}
            """)
            inp.textChanged.connect(lambda: self.answer_changed.emit())

            rl.addWidget(lbl)
            rl.addWidget(inp, stretch=1)
            self.tokens_layout.addWidget(row)
            self.token_inputs[token] = inp

    def get_answer(self) -> dict:
        return {"answers": {t: inp.text() for t, inp in self.token_inputs.items()}}

    def set_answer(self, data: dict):
        for token, text in data.get("answers", {}).items():
            if token in self.token_inputs:
                self.token_inputs[token].setText(text)

    def set_readonly(self, readonly: bool):
        super().set_readonly(readonly)
        for inp in self.token_inputs.values():
            inp.setReadOnly(readonly)
