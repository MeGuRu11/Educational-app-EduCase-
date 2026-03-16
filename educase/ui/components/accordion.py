# ui/components/accordion.py
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import QFrame, QPushButton, QScrollArea, QVBoxLayout, QWidget

from ui.styles.theme import COLORS


class AccordionSection(QWidget):
    """
    Разворачивающаяся секция (одна вкладка).
    """
    def __init__(self, title: str, content_widget: QWidget, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header button
        self.toggle_btn = QPushButton(f"▼ {title}")
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 12px;
                background-color: {COLORS['bg_layer']};
                border: 1px solid {COLORS['stroke_card']};
                border-radius: 6px;
                font-weight: bold;
                color: {COLORS['text_primary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['stroke_divider']};
            }}
        """)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.toggled.connect(self._toggle)

        # Content frame
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['stroke_card']};
                border-top: none;
                border-bottom-left-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
        """)

        content_layout = QVBoxLayout(self.content_frame)
        content_layout.addWidget(content_widget)

        # Initial state (collapsed)
        self.content_frame.setMaximumHeight(0)
        self.content_height = content_layout.sizeHint().height() + 24

        self.main_layout.addWidget(self.toggle_btn)
        self.main_layout.addWidget(self.content_frame)

    def _toggle(self, checked):
        # Анимация высоты
        self.anim = QPropertyAnimation(self.content_frame, b"maximumHeight")
        self.anim.setDuration(250)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        if checked:
            self.toggle_btn.setText(self.toggle_btn.text().replace("▼", "▲"))
            self.anim.setStartValue(0)
            self.anim.setEndValue(max(self.content_height, 200)) # Approximate content height
        else:
            self.toggle_btn.setText(self.toggle_btn.text().replace("▲", "▼"))
            self.anim.setStartValue(max(self.content_height, 200))
            self.anim.setEndValue(0)

        self.anim.start()

class Accordion(QScrollArea):
    """
    Аккордеон, содержащий несколько AccordionSection.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.container)

    def add_section(self, title: str, widget: QWidget):
        section = AccordionSection(title, widget)
        self.container_layout.addWidget(section)
