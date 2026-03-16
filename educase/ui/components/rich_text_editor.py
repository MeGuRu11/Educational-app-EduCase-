# ui/components/rich_text_editor.py
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextListFormat
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QTextEdit, QVBoxLayout, QWidget

from ui.styles.theme import COLORS


class RichTextEditor(QWidget):
    """
    Простой WYSIWYG редактор для форматирования текста заданий.
    """
    text_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self._setup_toolbar()

        self.editor = QTextEdit()
        self.editor.textChanged.connect(self.text_changed.emit)
        font = QFont("Segoe UI Variable", 11)
        self.editor.setFont(font)
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['stroke_control']};
                border-top: none;
                border-bottom-left-radius: 6px;
                border-bottom-right-radius: 6px;
                padding: 12px;
            }}
            QTextEdit:focus {{
                border: 1px solid {COLORS['accent']};
                border-top: none;
            }}
        """)

        self.main_layout.addWidget(self.editor)

    def _setup_toolbar(self):
        self.toolbar = QWidget()
        self.toolbar.setFixedHeight(40)
        self.toolbar.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_layer']};
                border: 1px solid {COLORS['stroke_control']};
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }}
            QPushButton:hover {{
                background: {COLORS['stroke_card']};
            }}
        """)

        tb_layout = QHBoxLayout(self.toolbar)
        tb_layout.setContentsMargins(8, 4, 8, 4)
        tb_layout.setSpacing(4)

        # Bold
        self.btn_bold = QPushButton()
        self.btn_bold.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_bold.setCheckable(True)
        self.btn_bold.clicked.connect(self._toggle_bold)

        # Italic
        self.btn_italic = QPushButton()
        self.btn_italic.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_italic.setCheckable(True)
        self.btn_italic.clicked.connect(self._toggle_italic)

        # Bullet list
        self.btn_list = QPushButton()
        self.btn_list.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_list.clicked.connect(self._toggle_list)

        self.btn_bold.setText("B")
        self.btn_bold.setStyleSheet("font-weight: bold;")
        self.btn_italic.setText("I")
        self.btn_italic.setStyleSheet("font-style: italic;")
        self.btn_list.setText("• Задать список")

        tb_layout.addWidget(self.btn_bold)
        tb_layout.addWidget(self.btn_italic)
        tb_layout.addWidget(self.btn_list)
        tb_layout.addStretch()

        self.main_layout.addWidget(self.toolbar)

    def _toggle_bold(self):
        fmt = self.editor.currentCharFormat()
        weight = QFont.Weight.Bold if self.btn_bold.isChecked() else QFont.Weight.Normal
        fmt.setFontWeight(weight)
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_italic(self):
        fmt = self.editor.currentCharFormat()
        fmt.setFontItalic(self.btn_italic.isChecked())
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_list(self):
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        if cursor.currentList():
            block_fmt = cursor.blockFormat()
            cursor.setBlockFormat(block_fmt)
        else:
            list_fmt = QTextListFormat()
            list_fmt.setStyle(QTextListFormat.Style.ListDisc)
            cursor.createList(list_fmt)
        cursor.endEditBlock()

    def get_html(self) -> str:
        return self.editor.toHtml()

    def set_html(self, html: str):
        self.editor.setHtml(html)
