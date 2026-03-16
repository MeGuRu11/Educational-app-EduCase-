# ui/components/table_view.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QTableWidget

from ui.styles.theme import COLORS


class TableView(QTableWidget):
    """
    Конфигурируемая таблица с нашими стилями:
    полосатая раскраска (striped), эффекты наведения, скрытие рамок внутри.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Stretch last column
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.verticalHeader().setVisible(False)

        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
                border: none;
                color: {COLORS['text_primary']};
                gridline-color: {COLORS['stroke_divider']};
                font-family: "Segoe UI Variable";
                font-size: 14px;
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {COLORS['stroke_divider']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['info_bg']};
                color: {COLORS['text_primary']};
            }}
            QHeaderView::section {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                font-weight: bold;
                padding: 12px;
                border: none;
                border-bottom: 2px solid {COLORS['stroke_divider']};
            }}
        """)
