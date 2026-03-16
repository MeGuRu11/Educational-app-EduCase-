# ui/components/badge.py
from typing import Literal

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ui.styles.theme import COLORS


class Badge(QWidget):
    """
    Метка статуса (например: "Новое", "В процессе", "Завершено").
    """
    def __init__(self, text: str, type_: Literal["accent", "primary", "success", "warning", "error", "neutral"] = "neutral", parent=None):
        super().__init__(parent)
        self.text = text

        if type_ == "primary":
            self.type_ = "accent"
        else:
            self.type_ = type_

        # Determine colors based on type
        if self.type_ == "neutral":
            self.bg_color = COLORS["bg_elevated"]
            self.text_color = COLORS["text_secondary"]
        elif self.type_ == "accent":
            self.bg_color = COLORS["info_bg"]
            self.text_color = COLORS["accent"]
        else:
            self.bg_color = COLORS[f"{self.type_}_bg"]
            self.text_color = COLORS[self.type_]

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self.label = QLabel(self.text)
        font = QFont("Segoe UI Variable", 9)
        font.setBold(True)
        self.label.setFont(font)

        self.label.setStyleSheet(f"""
            QLabel {{
                color: {self.text_color};
                background: transparent;
            }}
        """)

        self.setStyleSheet(f"""
            Badge {{
                background-color: {self.bg_color};
                border-radius: 12px;
            }}
        """)

        layout.addWidget(self.label)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(24)
