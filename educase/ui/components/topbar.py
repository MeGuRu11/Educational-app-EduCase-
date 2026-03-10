# ui/components/topbar.py
"""
Верхняя панель (Topbar) для QStackedWidget.
Отвечает за drag окна (если MainWindow Frameless), заголовок и дополнительные действия.
"""
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QMouseEvent, QFont, QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QApplication, QWidget

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
        from ui.components.window_controls import WindowControls
        self.window_controls = WindowControls(show_maximize=True)
        self.window_controls.minimized.connect(self.minimized.emit)
        self.window_controls.maximized.connect(self.maximized.emit)
        self.window_controls.closed.connect(self.closed.emit)
        layout.addWidget(self.window_controls)

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
