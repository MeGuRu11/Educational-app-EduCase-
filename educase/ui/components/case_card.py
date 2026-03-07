# ui/components/case_card.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from ui.components.card import Card
from ui.components.badge import Badge
from ui.styles.theme import COLORS

class CaseCard(Card):
    """
    Карточка учебного кейса.
    Содержит метку сложности, название, короткое описание и кнопку Действия.
    """
    def __init__(self, title: str, description: str, difficulty: int, parent=None):
        super().__init__(parent, hover_effect=True)
        self.setFixedSize(300, 220)
        
        layout = self.main_layout
        layout.setSpacing(12)
        
        # Difficulty Badge
        diff_text = {1: "Легкий", 2: "Средний", 3: "Сложный"}.get(difficulty, "Неизвестно")
        diff_type = {1: "success", 2: "warning", 3: "error"}.get(difficulty, "neutral")
        self.badge = Badge(diff_text, diff_type) # type: ignore
        
        # Title
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet(f"background: transparent; font-size: 16px; font-weight: bold; color: {COLORS['text_primary']}; border: none;")
        self.title_lbl.setWordWrap(True)
        
        # Description
        self.desc_lbl = QLabel(description)
        self.desc_lbl.setStyleSheet(f"background: transparent; color: {COLORS['text_secondary']}; border: none;")
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # Action button
        self.btn_action = QPushButton("Начать")
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_action.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_hover']};
            }}
        """)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.badge, 0, Qt.AlignmentFlag.AlignLeft)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.desc_lbl, 1) # stretch 1
        layout.addWidget(self.btn_action)
