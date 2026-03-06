# ui/components/stat_card.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

from ui.components.card import Card
from ui.styles.theme import COLORS
from ui.styles.icons import get_icon

class StatCard(Card):
    """
    Карточка статистики (Значение + Описание + Иконка).
    """
    def __init__(self, value: str, label: str, icon_name: str, color_type: str = "accent", parent=None):
        super().__init__(parent, hover_effect=False)
        self.setFixedHeight(120)
        
        main_layout = self.main_layout
        
        top_layout = QHBoxLayout()
        
        # Значение
        self.val_lbl = QLabel(str(value))
        self.val_lbl.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLORS['text_primary']}; border: none;")
        
        # Иконка
        icon_color = COLORS.get(color_type, COLORS["accent"])
        self.icon_lbl = QLabel()
        self.icon_lbl.setPixmap(get_icon(icon_name, icon_color).pixmap(32, 32))
        
        top_layout.addWidget(self.val_lbl)
        top_layout.addStretch()
        top_layout.addWidget(self.icon_lbl)
        
        # Описание
        self.desc_lbl = QLabel(label)
        self.desc_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
        
        main_layout.addLayout(top_layout)
        main_layout.addStretch()
        main_layout.addWidget(self.desc_lbl)
