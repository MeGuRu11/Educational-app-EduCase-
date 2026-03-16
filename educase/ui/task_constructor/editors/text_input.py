# ui/task_constructor/editors/text_input.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QCheckBox, QFrame
)
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon
from ..base_editor import AbstractTaskEditor

class CustomCheckBox(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("QPushButton { border: none; background: transparent; outline: none; margin: 0; padding: 0; }")
        
        from PySide6.QtCore import QSize
        self.icon_uncheck = get_icon("checkbox_uncheck", COLORS["stroke_control"], 24)
        self.icon_hover   = get_icon("checkbox_uncheck", COLORS["accent"], 24)
        self.icon_check   = get_icon("checkbox_check", COLORS["accent"], 24)
        
        self.setIcon(self.icon_uncheck)
        self.setIconSize(QSize(24, 24))
        self.toggled.connect(self._update_icon)
        
    def _update_icon(self, checked):
        if checked:
            self.setIcon(self.icon_check)
        else:
            self.setIcon(self.icon_uncheck)
            
    def enterEvent(self, event):
        if not self.isChecked():
            self.setIcon(self.icon_hover)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        if not self.isChecked():
            self.setIcon(self.icon_uncheck)
        super().leaveEvent(event)

class TextInputEditor(AbstractTaskEditor):
    """
    Редактор для задания типа "Ввод текста" (text_input).
    Позволяет добавлять варианты правильных ответов (синонимы/опечатки)
    и настраивать чувствительность к регистру.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.answers = [] # Список dict: {"id": str, "widget": QWidget, "input": QLineEdit}
        self.answer_counter = 0
        
        self._setup_options_ui()
        
    def _setup_options_ui(self):
        # ── Блок вариантов ответа ──
        self.options_group = QWidget()
        self.options_layout = QVBoxLayout(self.options_group)
        self.options_layout.setContentsMargins(0, 16, 0, 0)
        self.options_layout.setSpacing(8)
        
        title_layout = QHBoxLayout()
        title = QLabel("Правильные варианты ответа (ученику достаточно ввести один из них)")
        title.setWordWrap(True)
        title.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']};")
        title_layout.addWidget(title)
        
        case_container = QWidget()
        case_layout = QHBoxLayout(case_container)
        case_layout.setContentsMargins(0, 0, 0, 0)
        case_layout.setSpacing(8)
        case_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.cb_case_sensitive = CustomCheckBox()
        self.cb_case_sensitive.toggled.connect(lambda: self.data_changed.emit())
        
        cb_label = QLabel("Учитывать регистр (а ≠ А)")
        cb_label.setCursor(Qt.CursorShape.PointingHandCursor)
        cb_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        cb_label.mousePressEvent = lambda e: self.cb_case_sensitive.toggle()
        
        case_layout.addWidget(self.cb_case_sensitive)
        case_layout.addWidget(cb_label)
        case_layout.addStretch()
        
        title_layout.addWidget(case_container)
        self.options_layout.addLayout(title_layout)
        
        # Контейнер для списка 
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.options_layout.addWidget(self.list_container)
        
        # Кнопка добавления варианта
        self.btn_add = QPushButton("+ Добавить допустимый ответ")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg_layer']};
                color: {COLORS['accent']};
                border: 1px dashed {COLORS['stroke_control']};
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['state_hover']};
                border-color: {COLORS['accent']};
            }}
        """)
        self.btn_add.clicked.connect(self._add_empty_answer)
        self.options_layout.addWidget(self.btn_add)
        
        # Вставляем блок вариантов
        self.main_layout.insertWidget(2, self.options_group)
        
        # Добавим один пустой вариант
        self._add_empty_answer()

    def _add_empty_answer(self):
        ans_id = f"ans_{self.answer_counter}"
        self.answer_counter += 1
        
        row = QFrame()
        row.setStyleSheet(f"background: {COLORS['bg_elevated']}; border: 1px solid {COLORS['stroke_divider']}; border-radius: 6px;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(12, 8, 12, 8)
        
        # Индикатор (буллит)
        bullet = QLabel("•")
        bullet.setStyleSheet(f"color: {COLORS['text_disabled']}; font-size: 16px; font-weight: bold;")
        row_layout.addWidget(bullet)
            
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Введите правильный ответ (например: Кошка)")
        line_edit.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
            QLineEdit:focus {{ outline: none; }}
        """)
        line_edit.textChanged.connect(lambda: self.data_changed.emit())
        
        btn_del = QPushButton()
        btn_del.setIcon(get_icon("delete", COLORS["error"], 18))
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet("border: none; background: transparent; padding: 4px;")
        btn_del.clicked.connect(lambda: self._remove_answer(ans_id))
        
        row_layout.addWidget(line_edit, stretch=1)
        row_layout.addWidget(btn_del)
        
        self.list_layout.addWidget(row)
        
        self.answers.append({
            "id": ans_id,
            "widget": row,
            "input": line_edit
        })
        
        self.data_changed.emit()

    def _remove_answer(self, ans_id: str):
        if len(self.answers) <= 1:
            return  # Нужно сохранить хотя бы один ответ
            
        target_ans = next((a for a in self.answers if a["id"] == ans_id), None)
        if target_ans:
            self.list_layout.removeWidget(target_ans["widget"])
            target_ans["widget"].deleteLater()
            self.answers.remove(target_ans)
            self.data_changed.emit()

    def get_specific_data(self) -> dict:
        valid_answers = [a["input"].text().strip() for a in self.answers if a["input"].text().strip()]
        return {
            "correct_answers": valid_answers,
            "case_sensitive": self.cb_case_sensitive.isChecked()
        }

    def set_specific_data(self, data: dict):
        # Настройки
        self.cb_case_sensitive.setChecked(data.get("case_sensitive", False))
        
        # Очищаем существующие (обходим ограничение min-1)
        for ans in list(self.answers):
            self.list_layout.removeWidget(ans["widget"])
            ans["widget"].deleteLater()
            
        self.answers.clear()
        self.answer_counter = 0
        
        answers_data = data.get("correct_answers", [])
        if not answers_data:
            self._add_empty_answer()
            return
            
        for text in answers_data:
            self._add_empty_answer()
            self.answers[-1]["input"].setText(text)
