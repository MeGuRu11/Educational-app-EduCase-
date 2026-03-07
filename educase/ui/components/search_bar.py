# ui/components/search_bar.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon

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
        
        # Focus effects tracking
        self.input.installEventFilter(self)
        self._is_focused = False

    def eventFilter(self, obj, event):
        if obj == self.input:
            if event.type() == event.Type.FocusIn:
                self._is_focused = True
                self.icon_lbl.setPixmap(get_icon("search", COLORS["accent"]).pixmap(18, 18))
                self.update()
            elif event.type() == event.Type.FocusOut:
                self._is_focused = False
                self.icon_lbl.setPixmap(get_icon("search", COLORS["text_secondary"]).pixmap(18, 18))
                self.update()
        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        rect = self.rect().adjusted(1, 1, -1, -1)
        radius = (self.height() - 2) / 2.0
        path.addRoundedRect(rect, radius, radius)
        
        p.fillPath(path, QColor(COLORS["bg_elevated"]))
        
        # Border
        if self._is_focused:
            p.setPen(QColor(COLORS["accent"]))
        else:
            p.setPen(QColor(0, 0, 0, 36)) # stroke_control
            
        p.drawPath(path)
