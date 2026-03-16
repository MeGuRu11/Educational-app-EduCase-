# ui/task_constructor/base_editor.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QSpinBox, QDoubleSpinBox, QFormLayout, QGroupBox, QLineEdit
)
from PySide6.QtCore import Qt, Signal

from ui.components.rich_text_editor import RichTextEditor
from ui.styles.theme import COLORS

class AbstractTaskEditor(QWidget):
    """
    Базовый класс для всех редакторов заданий.
    Обеспечивает общее поле условия (RichText) и настройки баллов.
    Наследники должны реализовать _setup_specific_ui(), get_task_data() и set_task_data().
    """
    data_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(16)
        # Убираем background: bg_layer отсюда, зададим его в контейнере, если нужно
        
        # 1. Заголовок
        header_lbl = QLabel("Условие задания:")
        header_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text_primary']};")
        self.main_layout.addWidget(header_lbl)
        
        # 2. Поле условия (RichTextEditor)
        self.body_editor = RichTextEditor()
        self.body_editor.text_changed.connect(self.data_changed.emit)
        self.main_layout.addWidget(self.body_editor, stretch=1)
        
        # 3. Специфичный UI для конкретного типа (вставляется наследником)
        self.specific_layout = QVBoxLayout()
        self.specific_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.specific_layout, stretch=2)
        self._setup_specific_ui(self.specific_layout)
        
        # 4. Общие настройки (Баллы, Подсказки)
        self.main_layout.addWidget(self._create_settings_group())

    def _create_settings_group(self) -> QGroupBox:
        group = QGroupBox("Настройки оценивания и обратной связи")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }}
        """)
        
        fl_layout = QFormLayout(group)
        fl_layout.setSpacing(12)
        
        # Максимальный балл
        self.max_score_spin = QDoubleSpinBox()
        self.max_score_spin.setRange(0.0, 100.0)
        self.max_score_spin.setValue(10.0)
        self.max_score_spin.valueChanged.connect(lambda: self.data_changed.emit())
        
        # Штрафной балл
        self.penalty_spin = QDoubleSpinBox()
        self.penalty_spin.setRange(0.0, 100.0)
        self.penalty_spin.setValue(0.0)
        self.penalty_spin.valueChanged.connect(lambda: self.data_changed.emit())
        
        # Частичный балл (да/нет или процент, пока просто чекбокс или комбо - сделаем через 0/1 так как в базе INTEGER)
        from PySide6.QtWidgets import QCheckBox
        self.partial_credit_chk = QCheckBox("Разрешить частичный балл")
        self.partial_credit_chk.toggled.connect(lambda: self.data_changed.emit())
        
        score_layout = QHBoxLayout()
        score_layout.addWidget(QLabel("Макс. балл:"))
        score_layout.addWidget(self.max_score_spin)
        score_layout.addSpacing(16)
        score_layout.addWidget(QLabel("Штраф:"))
        score_layout.addWidget(self.penalty_spin)
        score_layout.addStretch()
        
        fl_layout.addRow(score_layout)
        fl_layout.addRow(self.partial_credit_chk)
        
        # Подсказки
        self.hint_input = QLineEdit()
        self.hint_input.setPlaceholderText("Подсказка до ответа (опционально)")
        self.hint_input.textChanged.connect(self.data_changed.emit)
        
        self.explanation_input = QLineEdit()
        self.explanation_input.setPlaceholderText("Объяснение после ответа (опционально)")
        self.explanation_input.textChanged.connect(self.data_changed.emit)
        
        fl_layout.addRow("Подсказка 💡:", self.hint_input)
        fl_layout.addRow("Объяснение 💬:", self.explanation_input)
        
        return group

    def _setup_specific_ui(self, layout: QVBoxLayout):
        """Переопределяется в наследниках для добавления своих полей ввода."""
        pass

    def get_data(self) -> dict:
        """Собирает общие и специфичные данные."""
        data = {
            "body": self.body_editor.get_html(),
            "max_score": self.max_score_spin.value(),
            "penalty_score": self.penalty_spin.value(),
            "partial_credit": 1 if self.partial_credit_chk.isChecked() else 0,
            "hint_text": self.hint_input.text(),
            "explanation": self.explanation_input.text()
        }
        # Добавляем данные от наследника
        specific_data = self.get_specific_data()
        data.update(specific_data)
        return data

    def get_specific_data(self) -> dict:
        """Переопределяется в наследниках. Возвращает dict со специфичными настройками."""
        return {}

    def set_data(self, data: dict):
        """Заполняет общие и специфичные данные."""
        self.body_editor.set_html(data.get("body", ""))
        self.max_score_spin.setValue(float(data.get("max_score", 10.0)))
        self.penalty_spin.setValue(float(data.get("penalty_score", 0.0)))
        self.partial_credit_chk.setChecked(bool(data.get("partial_credit", 0)))
        self.hint_input.setText(data.get("hint_text", "") or "")
        self.explanation_input.setText(data.get("explanation", "") or "")
        
        self.set_specific_data(data)

    def set_specific_data(self, data: dict):
        """Переопределяется в наследниках. Заполняет форму из dict."""
        pass
