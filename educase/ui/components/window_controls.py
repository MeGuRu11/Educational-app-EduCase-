# ui/components/window_controls.py
"""
Кнопки управления окном в стиле Windows 10/11.
Используем простые Unicode-символы, которые гарантированно отображаются.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.styles.theme import COLORS


class WindowControls(QWidget):
    """
    Универсальный виджет с кнопками управления окном
    в стиле стандартных Windows 10/11 chrome buttons.
    """
    minimized = Signal()
    maximized = Signal()
    closed = Signal()

    def __init__(self, parent=None, show_maximize=True):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Шрифт для символов
        btn_font = QFont("Segoe UI", 10)

        # Общие стили для кнопок (hover как в Windows)
        base_style = f"""
            QPushButton {{
                border: none;
                background: transparent;
                color: {COLORS['text_primary']};
                font-size: 14px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background: rgba(0, 0, 0, 0.05);
            }}
            QPushButton:pressed {{
                background: rgba(0, 0, 0, 0.08);
            }}
        """

        close_style = f"""
            QPushButton {{
                border: none;
                background: transparent;
                color: {COLORS['text_primary']};
                font-size: 14px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background: #E81123;
                color: white;
            }}
            QPushButton:pressed {{
                background: #F1707A;
                color: white;
            }}
        """

        # Кнопка Свернуть (горизонтальная линия)
        self.btn_min = QPushButton("\u2500")  # ─
        self.btn_min.setFont(btn_font)
        self.btn_min.setFixedSize(46, 32)
        self.btn_min.setCursor(Qt.CursorShape.ArrowCursor)
        self.btn_min.setStyleSheet(base_style)
        self.btn_min.clicked.connect(self.minimized.emit)
        layout.addWidget(self.btn_min)

        # Кнопка Развернуть (опционально)
        if show_maximize:
            self.btn_max = QPushButton("\u25A1")  # □
            self.btn_max.setFont(btn_font)
            self.btn_max.setFixedSize(46, 32)
            self.btn_max.setCursor(Qt.CursorShape.ArrowCursor)
            self.btn_max.setStyleSheet(base_style)
            self.btn_max.clicked.connect(self.maximized.emit)
            layout.addWidget(self.btn_max)

        # Кнопка Закрыть (крестик)
        self.btn_close = QPushButton("\u2715")  # ✕
        self.btn_close.setFont(btn_font)
        self.btn_close.setFixedSize(46, 32)
        self.btn_close.setCursor(Qt.CursorShape.ArrowCursor)
        self.btn_close.setStyleSheet(close_style)
        self.btn_close.clicked.connect(self.closed.emit)
        layout.addWidget(self.btn_close)

    def set_maximized_icon(self, is_maximized: bool):
        """Переключает иконку кнопки между Maximize и Restore."""
        if hasattr(self, 'btn_max'):
            self.btn_max.setText("\u29C9" if is_maximized else "\u25A1")  # ⧉ vs □
