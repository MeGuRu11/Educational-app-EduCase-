# ui/components/score_badge.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtGui import QFont, QPainter, QPainterPath, QColor
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon

class ScoreBadge(QWidget):
    """
    Бейдж для отображения баллов с иконкой звездочки.
    Например: "8/10"
    """
    def __init__(self, score: float, max_score: float, parent=None):
        super().__init__(parent)
        self.score = score
        self.max_score = max_score
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        
        # Иконка
        icon_label = QLabel()
        icon = get_icon("star", COLORS["warning"])
        icon_label.setPixmap(icon.pixmap(14, 14))
        icon_label.setStyleSheet("background: transparent;")
        
        # Текст
        text_label = QLabel(f"{self.score:g} / {self.max_score:g}")
        font = QFont("Segoe UI Variable", 9)
        font.setBold(True)
        text_label.setFont(font)
        text_label.setStyleSheet(f"background: transparent; color: {COLORS['warning']};")
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        
        self.setStyleSheet(f"""
            ScoreBadge {{
                background-color: {COLORS['warning_bg']};
                border-radius: 12px;
            }}
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(24)
