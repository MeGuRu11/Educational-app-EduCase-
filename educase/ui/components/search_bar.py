# ui/components/search_bar.py
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget

from ui.styles.icons import get_icon
from ui.styles.theme import COLORS


class SearchBar(QWidget):
    """
    Поле поиска с иконкой лупы.
    Возможность анимированного расширения при получении фокуса.
    """
    def __init__(self, placeholder="Поиск...", parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        # Icon
        self.icon_lbl = QLabel()
        self.icon_lbl.setStyleSheet("background: transparent;")
        self.icon_lbl.setPixmap(get_icon("search", COLORS["text_secondary"]).pixmap(18, 18))

        # Input
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                padding: 0px;
                padding-bottom: 2px;
                color: {COLORS['text_primary']};
                font-family: "Segoe UI Variable";
                font-size: 14px;
            }}
        """)

        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.input)

        self._is_focused = False
        self.input.installEventFilter(self)
        self.update_style()

    def eventFilter(self, obj, event):
        if obj == self.input:
            if event.type() == event.Type.FocusIn:
                self._is_focused = True
                self.icon_lbl.setPixmap(get_icon("search", COLORS["accent"]).pixmap(18, 18))
                self.update_style()
            elif event.type() == event.Type.FocusOut:
                self._is_focused = False
                self.icon_lbl.setPixmap(get_icon("search", COLORS["text_secondary"]).pixmap(18, 18))
                self.update_style()
        return super().eventFilter(obj, event)

    def update_style(self):
        border_color = COLORS["accent"] if self._is_focused else "rgba(0, 0, 0, 0.14)"
        self.setStyleSheet(f"""
            SearchBar {{
                background-color: {COLORS["bg_elevated"]};
                border: 1px solid {border_color};
                border-radius: 18px;
            }}
        """)
