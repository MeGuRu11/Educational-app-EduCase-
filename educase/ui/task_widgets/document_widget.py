# ui/task_widgets/document_widget.py
"""Виджет задания «Анализ документа» — просмотр файла + поля ответов."""
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout, QWidget
)
from PySide6.QtCore import Qt
import os

from ui.styles.theme import COLORS
from .base_task_widget import BaseTaskWidget


class DocumentWidget(BaseTaskWidget):
    def _setup_answer_ui(self, layout: QVBoxLayout):
        # Кнопка открытия документа
        doc_row = QHBoxLayout()
        self.btn_open_doc = QPushButton("📄 Открыть документ")
        self.btn_open_doc.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_doc.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
            }}
            QPushButton:hover {{ background: #1565C0; }}
        """)
        self.btn_open_doc.clicked.connect(self._open_document)
        doc_row.addWidget(self.btn_open_doc)
        doc_row.addStretch()
        layout.addLayout(doc_row)

        self._doc_path = ""

        # Вопросы (создаются при set_task)
        self.questions_layout = QVBoxLayout()
        self.questions_layout.setSpacing(10)
        layout.addLayout(self.questions_layout)
        self.question_inputs: list[QLineEdit] = []

    def set_task(self, task_data: dict):
        super().set_task(task_data)
        for inp in self.question_inputs:
            inp.parent().deleteLater() if inp.parent() else inp.deleteLater()
        self.question_inputs.clear()

        config = task_data.get("configuration", {})
        self._doc_path = config.get("document_path", "")
        questions = config.get("questions", [])

        self.btn_open_doc.setVisible(bool(self._doc_path))

        for i, q in enumerate(questions):
            card = QWidget()
            card.setStyleSheet(f"""
                QWidget {{
                    background: {COLORS['bg_elevated']};
                    border: 1px solid {COLORS['stroke_divider']};
                    border-radius: 8px;
                }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)

            q_label = QLabel(f"{i+1}. {q.get('question', '')}")
            q_label.setWordWrap(True)
            q_label.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']}; border: none;")
            cl.addWidget(q_label)

            inp = QLineEdit()
            inp.setPlaceholderText("Введите ответ...")
            inp.setStyleSheet(f"""
                QLineEdit {{
                    border: 1px solid {COLORS['stroke_control']};
                    border-radius: 4px;
                    padding: 8px 12px;
                    background: {COLORS['bg_layer']};
                    color: {COLORS['text_primary']};
                }}
                QLineEdit:focus {{ border-color: {COLORS['accent']}; }}
            """)
            inp.textChanged.connect(lambda: self.answer_changed.emit())
            cl.addWidget(inp)

            self.questions_layout.addWidget(card)
            self.question_inputs.append(inp)

    def get_answer(self) -> dict:
        return {"answers": [inp.text() for inp in self.question_inputs]}

    def set_answer(self, data: dict):
        answers = data.get("answers", [])
        for i, text in enumerate(answers):
            if i < len(self.question_inputs):
                self.question_inputs[i].setText(str(text))

    def _open_document(self):
        if self._doc_path and os.path.exists(self._doc_path):
            os.startfile(self._doc_path)

    def set_readonly(self, readonly: bool):
        super().set_readonly(readonly)
        for inp in self.question_inputs:
            inp.setReadOnly(readonly)
