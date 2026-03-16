# ui/task_constructor/type_selector.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton,
    QButtonGroup
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon

TASK_TYPES = [
    {"id": "single_choice", "name": "Один ответ", "icon": "check_circle"},
    {"id": "multi_choice", "name": "Несколько ответов", "icon": "check"},
    {"id": "text_input", "name": "Ввод текста", "icon": "edit"},
    {"id": "form_fill", "name": "Заполнение формы", "icon": "document"},
    {"id": "ordering", "name": "Сортировка", "icon": "sort"},
    {"id": "matching", "name": "Соответствия", "icon": "module"},
    {"id": "calculation", "name": "Вычисление", "icon": "formula"},
    {"id": "image_annotation", "name": "Зоны на изображении", "icon": "image"},
    {"id": "timeline", "name": "Таймлайн", "icon": "timeline"},
    {"id": "table_input", "name": "Таблица", "icon": "table"},
    {"id": "document_editor", "name": "Анализ документа", "icon": "book"},
    {"id": "branching", "name": "Ветвление сценария", "icon": "branch"},
]

class TypeSelector(QWidget):
    """
    Левая панель выбора типа задания. 12 вариантов.
    Эмитит сигнал type_selected(str) с ID выбранного типа.
    """
    type_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(240)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Заголовок
        header = QLabel("Тип задания")
        header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text_primary']}; padding: 16px;")
        self.main_layout.addWidget(header)
        
        # Область прокрутки
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(12, 0, 12, 16)
        self.scroll_layout.setSpacing(8)
        
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self.btn_group.idToggled.connect(self._on_button_toggled)
        
        self.buttons = {}
        
        for idx, t in enumerate(TASK_TYPES):
            btn = QPushButton(t["name"])
            icon = get_icon(t["icon"], COLORS["text_secondary"], 20)
            btn.setIcon(icon)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Стилизация кнопки как карточки
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 12px 16px;
                    border: 1px solid transparent;
                    border-radius: 6px;
                    background: transparent;
                    color: {COLORS['text_secondary']};
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background: {COLORS['bg_layer']};
                    color: {COLORS['text_primary']};
                }}
                QPushButton:checked {{
                    background: {COLORS['bg_layer']};
                    border: 1px solid {COLORS['accent']};
                    color: {COLORS['accent']};
                    font-weight: bold;
                }}
            """)
            
            self.btn_group.addButton(btn, id=idx)
            self.scroll_layout.addWidget(btn)
            self.buttons[t["id"]] = btn
            
        self.scroll_layout.addStretch()
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

    def _on_button_toggled(self, btn_id: int, checked: bool):
        if checked:
            task_type_id = TASK_TYPES[btn_id]["id"]
            
            # Обновляем цвет иконки на accent для выбранного
            for idx, t in enumerate(TASK_TYPES):
                btn = self.btn_group.button(idx)
                if idx == btn_id:
                    btn.setIcon(get_icon(t["icon"], COLORS["accent"], 20))
                else:
                    btn.setIcon(get_icon(t["icon"], COLORS["text_secondary"], 20))
                    
            self.type_selected.emit(task_type_id)

    def set_active_type(self, task_type_id: str):
        """Программно выбирает тип."""
        if task_type_id in self.buttons:
            self.buttons[task_type_id].setChecked(True)
