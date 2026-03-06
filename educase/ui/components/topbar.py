# ui/components/topbar.py
"""
Верхняя панель (Topbar) для QStackedWidget.
Отвечает за drag окна (если MainWindow Frameless), заголовок и дополнительные действия.
"""
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QMouseEvent, QFont, QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QApplication

from ui.styles.icons import get_icon
from ui.styles.theme import COLORS


class Topbar(QFrame):
    """Кастомный TitleBar (Frameless Window) с возможностью перетаскивания."""
    
    # Сигналы для кнопок управления окном
    minimized = Signal()
    maximized = Signal()
    closed = Signal()

    def __init__(self, main_window_widget: "QWidget"):
        super().__init__()
        self.main_window_widget = main_window_widget # Для перетаскивания всего окна
        
        self.setFixedHeight(56)
        self.setStyleSheet(f"background-color: {COLORS['bg_layer']}; border-bottom: 1px solid {COLORS['stroke_divider']};")
        
        self._drag_start_pos = QPoint()
        self._dragging = False
        
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 16, 0)
        layout.setSpacing(16)

        # ── Заголовок секции (динамический)
        self.lbl_title = QLabel("Главная")
        font = QFont("Segoe UI Variable", 18, QFont.Weight.Bold)
        self.lbl_title.setFont(font)
        self.lbl_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(self.lbl_title)

        layout.addStretch()

        # ── Контролы окна (min, max, close)
        self.btn_min = QPushButton()
        self.btn_min.setIcon(get_icon("drag_handle", COLORS["text_secondary"], 20)) # temp icon for min
        self.btn_min.setFixedSize(32, 32)
        self.btn_min.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_min.setStyleSheet("border: none; background: transparent;")
        self.btn_min.clicked.connect(self.minimized.emit)
        layout.addWidget(self.btn_min)

        self.btn_max = QPushButton()
        self.btn_max.setIcon(get_icon("module", COLORS["text_secondary"], 20)) # temp icon for max
        self.btn_max.setFixedSize(32, 32)
        self.btn_max.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_max.setStyleSheet("border: none; background: transparent;")
        self.btn_max.clicked.connect(self.maximized.emit)
        layout.addWidget(self.btn_max)

        self.btn_close = QPushButton()
        self.btn_close.setIcon(get_icon("error_circle", COLORS["text_secondary"], 20)) # temp icon for close
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("border: none; background: transparent;")
        self.btn_close.clicked.connect(self.closed.emit)
        layout.addWidget(self.btn_close)

    def set_title(self, text: str) -> None:
        self.lbl_title.setText(text)

    # ── Поддержка перетаскивания окна (Drag)
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            # Считаем смещение от верхнего левого угла ГЛАВНОГО окна
            self._drag_start_pos = event.globalPosition().toPoint() - self.main_window_widget.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._dragging:
            self.main_window_widget.move(event.globalPosition().toPoint() - self._drag_start_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._dragging = False
        event.accept()
