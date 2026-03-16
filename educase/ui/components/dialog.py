# ui/components/dialog.py
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QDialog,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.styles.theme import COLORS, RADIUS


class BaseDialog(QDialog):
    """
    Базовый стилизованный диалог без системных рамок с "затенением" фона.
    По умолчанию открывается модально на весь экран родителя и центрирует себя.
    """
    def __init__(self, parent=None, title=""):
        # Создаем прозрачное полноэкранное окно, чтобы перехватить клики и затенить фон
        super().__init__(parent)
        self.title_text = title
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Настраиваем размер по родителю
        if parent:
            self.resize(parent.size())

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._setup_dialog_box()

    def _setup_dialog_box(self):
        # Сам белый прямоугольник диалога
        self.box = QWidget()
        self.box.setFixedWidth(400)
        self.box.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_elevated']};
                border-radius: {RADIUS['dialog'] if 'dialog' in RADIUS else 8}px;
                border: 1px solid {COLORS['stroke_card']};
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self.box)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 8)
        self.box.setGraphicsEffect(shadow)

        self.box_layout = QVBoxLayout(self.box)
        self.box_layout.setContentsMargins(24, 24, 24, 24)
        self.box_layout.setSpacing(16)

        if self.title_text:
            title_lbl = QLabel(self.title_text)
            title_lbl.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {COLORS['text_primary']}; border: none;")
            self.box_layout.addWidget(title_lbl)

        self.main_layout.addWidget(self.box)

    def paintEvent(self, event):
        # Затенение фона
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0, 120))


class ConfirmDialog(BaseDialog):
    """Диалог с вопросом и кнопками Отмена / Подтвердить"""
    def __init__(self, parent=None, title="Подтверждение", text="Вы уверены?"):
        super().__init__(parent, title)

        desc = QLabel(text)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
        self.box_layout.addWidget(desc)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_ok = QPushButton("Подтвердить")
        self.btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ok.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_ok)
        self.box_layout.addLayout(btn_layout)
