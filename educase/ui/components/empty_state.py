# ui/components/empty_state.py

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from ui.styles.icons import get_icon
from ui.styles.theme import COLORS


class EmptyState(QWidget):
    """
    Заглушка для пустого экрана с иконкой, заголовком и подзаголовком.
    """
    def __init__(self, title: str, subtitle: str = "", icon_name: str = "inbox", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        # Icon
        self.icon_lbl = QLabel()
        self.icon_lbl.setStyleSheet("background: transparent;")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = get_icon(icon_name, COLORS["text_secondary"]).pixmap(64, 64)
        self.icon_lbl.setPixmap(pixmap)

        # Title
        self.title_lbl = QLabel(title)
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_lbl.setStyleSheet(f"background: transparent; font-size: 18px; font-weight: 600; color: {COLORS['text_primary']};")

        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.title_lbl)

        # Subtitle
        if subtitle:
            self.subtitle_lbl = QLabel(subtitle)
            self.subtitle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.subtitle_lbl.setWordWrap(True)
            self.subtitle_lbl.setStyleSheet(f"background: transparent; font-size: 14px; color: {COLORS['text_secondary']};")
            layout.addWidget(self.subtitle_lbl)

        self.action_btn: QPushButton | None = None

    def add_action_button(self, text: str, callback):
        self.action_btn = QPushButton(text)
        self.action_btn.clicked.connect(callback)
        self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        lay = self.layout()
        if lay is not None and isinstance(lay, QVBoxLayout):
            lay.addWidget(self.action_btn)
            lay.setAlignment(self.action_btn, Qt.AlignmentFlag.AlignHCenter)
