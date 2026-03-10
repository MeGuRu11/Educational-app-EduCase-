from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QFrame)
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon
from ..base_editor import AbstractTaskEditor

class MatchingEditor(AbstractTaskEditor):
    """
    Редактор для задания типа "Соответствия" (matching).
    Позволяет добавлять пары: Ключ — Значение.
    """
    def __init__(self, parent=None):
        self.pairs = [] # Список dict: {"id": str, "widget": QWidget, "left": QLineEdit, "right": QLineEdit}
        self.pair_counter = 0
        super().__init__(parent)
        
    def _setup_specific_ui(self, layout: QVBoxLayout):
        self.options_group = QWidget()
        self.options_layout = QVBoxLayout(self.options_group)
        self.options_layout.setContentsMargins(0, 16, 0, 0)
        self.options_layout.setSpacing(8)
        
        title = QLabel("Пары для соответствия (Понятие — Определение)")
        title.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']};")
        self.options_layout.addWidget(title)
        
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.options_layout.addWidget(self.list_container)
        
        self.btn_add = QPushButton("+ Добавить пару")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['accent']};
                font-weight: bold;
                border: 2px dashed {COLORS['accent']}40;
                border-radius: 6px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background: {COLORS['state_hover']};
                border-color: {COLORS['accent']};
            }}
        """)
        self.btn_add.clicked.connect(self._add_empty_pair)
        self.options_layout.addWidget(self.btn_add)
        
        layout.addWidget(self.options_group)
        
        # Добавим две пары по умолчанию
        self._add_empty_pair()
        self._add_empty_pair()

    def _add_empty_pair(self):
        pair_id = f"pair_{self.pair_counter}"
        self.pair_counter += 1
        
        row = QFrame()
        row.setStyleSheet(f"background: {COLORS['bg_elevated']}; border: 1px solid {COLORS['stroke_divider']}; border-radius: 6px;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(12, 8, 12, 8)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        row_layout.setSpacing(12)
        
        # Левое поле (Ключ)
        left_input = QLineEdit()
        left_input.setPlaceholderText("Понятие")
        left_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
            QLineEdit:focus {{ outline: none; }}
        """)
        left_input.textChanged.connect(lambda: self.data_changed.emit())
        
        # Иконка-стрелочка
        lbl_arrow = QLabel()
        lbl_arrow.setPixmap(get_icon("forward", COLORS["text_secondary"], 20).pixmap(20, 20))
        lbl_arrow.setFixedSize(24, 24)
        lbl_arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_arrow.setStyleSheet("border: none; background: transparent;")
        
        # Правое поле (Значение)
        right_input = QLineEdit()
        right_input.setPlaceholderText("Определение")
        right_input.setStyleSheet(left_input.styleSheet())
        right_input.textChanged.connect(lambda: self.data_changed.emit())
        
        btn_del = QPushButton()
        btn_del.setIcon(get_icon("delete", COLORS["error"], 18))
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet("border: none; background: transparent; padding: 4px; margin: 0;")
        btn_del.clicked.connect(lambda: self._remove_pair(pair_id))
        
        row_layout.addWidget(left_input, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)
        row_layout.addWidget(lbl_arrow, alignment=Qt.AlignmentFlag.AlignVCenter)
        row_layout.addWidget(right_input, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)
        row_layout.addWidget(btn_del, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        self.list_layout.addWidget(row)
        
        self.pairs.append({
            "id": pair_id,
            "widget": row,
            "left": left_input,
            "right": right_input
        })
        
        self.data_changed.emit()

    def _remove_pair(self, pair_id: str):
        if len(self.pairs) <= 2:
            return  # Для соответствия нужно минимум 2 пары
            
        target_pair = next((p for p in self.pairs if p["id"] == pair_id), None)
        if target_pair:
            self.list_layout.removeWidget(target_pair["widget"])
            target_pair["widget"].deleteLater()
            self.pairs.remove(target_pair)
            self.data_changed.emit()

    def get_specific_data(self) -> dict:
        pairs_data = []
        for p in self.pairs:
            left_text = p["left"].text().strip()
            right_text = p["right"].text().strip()
            if left_text or right_text:
                pairs_data.append({
                    "id": p["id"],
                    "left": left_text,
                    "right": right_text
                })
        return {"pairs": pairs_data}

    def set_specific_data(self, data: dict):
        for p in list(self.pairs):
            self._remove_pair(p["id"])
            
        pairs_data = data.get("pairs", [])
        if not pairs_data:
            self._add_empty_pair()
            self._add_empty_pair()
            return
            
        self.pair_counter = 0
        self.pairs.clear()
        
        for p in pairs_data:
            self._add_empty_pair()
            last_pair = self.pairs[-1]
            last_pair["left"].setText(p.get("left", ""))
            last_pair["right"].setText(p.get("right", ""))
