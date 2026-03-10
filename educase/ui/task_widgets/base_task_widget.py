# ui/task_widgets/base_task_widget.py
"""
Базовый виджет для отображения задания студенту.
Все 12 типов наследуют этот класс.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal

from ui.styles.theme import COLORS


class BaseTaskWidget(QWidget):
    """
    Базовый виджет задания для студента.
    Показывает условие + специфичный UI для ответа.

    Субклассы реализуют:
        _setup_answer_ui(layout)  — создание UI для ввода ответа
        get_answer() → dict       — сбор ответа студента
        set_answer(data: dict)    — восстановление ранее сохранённого ответа
        set_readonly(bool)        — блокировка UI после проверки
    """
    answer_changed = Signal()  # Эмитится при любом изменении ответа

    def __init__(self, parent=None):
        super().__init__(parent)
        self._task_data: dict = {}
        self._readonly = False
        self._build_base_ui()

    def _build_base_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                width: 6px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['stroke_control']};
                border-radius: 3px;
                min-height: 30px;
            }}
        """)

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(24, 20, 24, 20)
        self._content_layout.setSpacing(16)

        # Условие задания
        self.lbl_body = QLabel()
        self.lbl_body.setWordWrap(True)
        self.lbl_body.setTextFormat(Qt.TextFormat.RichText)
        self.lbl_body.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 15px;
            line-height: 1.5;
        """)
        self._content_layout.addWidget(self.lbl_body)

        # Разделитель
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {COLORS['stroke_divider']}; margin: 4px 0;")
        self._content_layout.addWidget(sep)

        # Область для ответа (субклассы добавляют свой UI)
        self.answer_layout = QVBoxLayout()
        self.answer_layout.setSpacing(12)
        self._content_layout.addLayout(self.answer_layout)

        # Hook для субклассов
        self._setup_answer_ui(self.answer_layout)

        self._content_layout.addStretch()

        scroll.setWidget(self._content)
        self.main_layout.addWidget(scroll)

    def set_task(self, task_data: dict):
        """Загружает задание для отображения."""
        self._task_data = task_data
        body = task_data.get("body", "") or task_data.get("title", "")
        self.lbl_body.setText(body)

    def get_answer(self) -> dict:
        """Возвращает ответ студента. Переопределяется в субклассах."""
        return {}

    def set_answer(self, data: dict):
        """Восстанавливает ранее сохранённый ответ. Переопределяется."""
        pass

    def set_readonly(self, readonly: bool):
        """Блокирует UI после проверки. Переопределяется."""
        self._readonly = readonly

    def _setup_answer_ui(self, layout: QVBoxLayout):
        """Hook для субклассов — создание UI ввода ответа."""
        pass
