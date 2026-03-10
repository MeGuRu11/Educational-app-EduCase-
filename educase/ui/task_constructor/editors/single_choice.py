# ui/task_constructor/editors/single_choice.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QRadioButton, QScrollArea, QFrame, QButtonGroup
)
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon
from ..base_editor import AbstractTaskEditor

class CustomRadioButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("QPushButton { border: none; background: transparent; outline: none; margin: 0; padding: 0; }")
        
        from PySide6.QtCore import QSize
        self.icon_uncheck = get_icon("radio_uncheck", COLORS["stroke_control"], 24)
        self.icon_hover   = get_icon("radio_uncheck", COLORS["accent"], 24)
        self.icon_check   = get_icon("radio_check", COLORS["accent"], 24)
        
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

class SingleChoiceEditor(AbstractTaskEditor):
    """
    Редактор для задания типа "Один ответ" (single_choice).
    Позволяет добавлять варианты ответов с радио-кнопками для выбора верного.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.options = [] # Список dict: {"id": str, "widget": QWidget, "radio": QRadioButton, "input": QLineEdit}
        self.option_counter = 0
        
        self._setup_options_ui()
        
    def _setup_options_ui(self):
        # ── Блок вариантов ответа ──
        self.options_group = QWidget()
        self.options_layout = QVBoxLayout(self.options_group)
        self.options_layout.setContentsMargins(0, 16, 0, 0)
        self.options_layout.setSpacing(8)
        
        title = QLabel("Варианты ответа")
        title.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']};")
        self.options_layout.addWidget(title)
        
        # Контейнер для списка (скроллируемый, если вариантов много)
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.options_layout.addWidget(self.list_container)
        
        # Группа кнопок, чтобы только один radio был выбран
        self.radio_group = QButtonGroup(self)
        self.radio_group.idToggled.connect(self._on_radio_toggled)
        
        # Кнопка добавления варианта
        self.btn_add = QPushButton("+ Добавить вариант")
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
        self.btn_add.clicked.connect(self._add_empty_option)
        self.options_layout.addWidget(self.btn_add)
        
        # Вставляем блок вариантов сразу после редактора body
        # Layout у base_editor -> layout, позиция: 2 (0=header, 1=body)
        self.layout.insertWidget(2, self.options_group)
        
        # Добавим два дефолтных варианта
        self._add_empty_option(is_correct=True)
        self._add_empty_option()

    def _add_empty_option(self, is_correct=False):
        opt_id = f"opt_{self.option_counter}"
        self.option_counter += 1
        
        row = QFrame()
        row.setStyleSheet(f"background: {COLORS['bg_elevated']}; border: 1px solid {COLORS['stroke_divider']}; border-radius: 6px;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(12, 8, 12, 8)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        radio = CustomRadioButton()
        self.radio_group.addButton(radio, id=len(self.options))
        if is_correct:
            radio.setChecked(True)
            
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(f"Вариант {len(self.options) + 1}")
        line_edit.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                color: {COLORS['text_primary']};
                font-size: 14px;
                padding-bottom: 2px;
            }}
            QLineEdit:focus {{ outline: none; }}
        """)
        line_edit.textChanged.connect(lambda: self.data_changed.emit())
        
        btn_del = QPushButton()
        btn_del.setIcon(get_icon("delete", COLORS["error"], 18))
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet("border: none; background: transparent; padding: 4px;")
        btn_del.clicked.connect(lambda: self._remove_option(opt_id))
        
        row_layout.addWidget(radio, alignment=Qt.AlignmentFlag.AlignVCenter)
        row_layout.addWidget(line_edit, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)
        row_layout.addWidget(btn_del, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        self.list_layout.addWidget(row)
        
        self.options.append({
            "id": opt_id,
            "widget": row,
            "radio": radio,
            "input": line_edit
        })
        
        self._update_placeholders()
        self.data_changed.emit()

    def _remove_option(self, opt_id: str):
        if len(self.options) <= 1:
            return  # Запрещаем удалять последний вариант
            
        target_opt = next((o for o in self.options if o["id"] == opt_id), None)
        if target_opt:
            was_checked = target_opt["radio"].isChecked()  # Сохраняем ДО deleteLater
            self.radio_group.removeButton(target_opt["radio"])
            self.list_layout.removeWidget(target_opt["widget"])
            target_opt["widget"].deleteLater()
            self.options.remove(target_opt)
            
            # Если удалили выбранный чекбокс, выбираем первый доступный
            if was_checked and self.options:
                self.options[0]["radio"].setChecked(True)
                
            self._update_placeholders()
            self.data_changed.emit()

    def _update_placeholders(self):
        for idx, opt in enumerate(self.options):
            opt["input"].setPlaceholderText(f"Вариант {idx + 1}")
            self.radio_group.setId(opt["radio"], idx)

    def _on_radio_toggled(self, opt_id: int, checked: bool):
        if checked:
            self.data_changed.emit()

    def get_specific_data(self) -> dict:
        formatted_options = []
        for opt in self.options:
            formatted_options.append({
                "id": opt["id"],
                "text": opt["input"].text().strip(),
                "is_correct": opt["radio"].isChecked()
            })
        return {"options": formatted_options}

    def set_specific_data(self, data: dict):
        # Очищаем существующие
        for opt in list(self.options):
            self.radio_group.removeButton(opt["radio"])
            self.list_layout.removeWidget(opt["widget"])
            opt["widget"].deleteLater()
            
        self.options.clear()
        self.option_counter = 0
        
        options_data = data.get("options", [])
        if not options_data:
            self._add_empty_option(is_correct=True)
            self._add_empty_option()
            return
            
        for opt_data in options_data:
            self._add_empty_option(is_correct=opt_data.get("is_correct", False))
            self.options[-1]["id"] = opt_data.get("id", self.options[-1]["id"])
            self.options[-1]["input"].setText(opt_data.get("text", ""))
