# ui/task_widgets/table_input_widget.py
"""Виджет задания «Таблица» — заполнение ячеек таблицы."""
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from .base_task_widget import BaseTaskWidget


class TableInputWidget(BaseTaskWidget):
    def _setup_answer_ui(self, layout: QVBoxLayout):
        lbl = QLabel("Заполните пустые ячейки таблицы:")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(lbl)

        self.table = QTableWidget()
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: 8px;
                background: {COLORS['bg_elevated']};
                gridline-color: {COLORS['stroke_divider']};
            }}
            QTableWidget::item {{
                padding: 6px 8px;
                color: {COLORS['text_primary']};
            }}
            QHeaderView::section {{
                background: {COLORS['bg_layer']};
                color: {COLORS['text_primary']};
                font-weight: bold;
                padding: 6px;
                border: none;
                border-bottom: 1px solid {COLORS['stroke_divider']};
            }}
        """)
        self.table.setMinimumHeight(200)
        self.table.cellChanged.connect(lambda: self.answer_changed.emit())
        layout.addWidget(self.table)

    def set_task(self, task_data: dict):
        super().set_task(task_data)
        self.table.blockSignals(True)

        config = task_data.get("configuration", {})
        cells = config.get("cells", [])
        header_row = config.get("header_row", True)
        header_col = config.get("header_col", False)

        if not cells:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.table.blockSignals(False)
            return

        data_start_row = 1 if header_row else 0
        data_start_col = 1 if header_col else 0

        rows = len(cells) - data_start_row
        cols = len(cells[0]) - data_start_col if cells else 0

        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)

        # Заголовки столбцов
        if header_row and cells:
            headers = [str(cells[0][c]) for c in range(data_start_col, len(cells[0]))]
            self.table.setHorizontalHeaderLabels(headers)

        # Заголовки строк
        if header_col:
            row_headers = [str(cells[r][0]) for r in range(data_start_row, len(cells))]
            self.table.setVerticalHeaderLabels(row_headers)

        # Данные — пропускаем заголовки, оставляем ячейки пустыми для ввода
        for r in range(rows):
            for c in range(cols):
                item = QTableWidgetItem("")  # Пустое для ввода студентом
                self.table.setItem(r, c, item)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.blockSignals(False)

        # Сохраняем маппинг для get_answer
        self._data_start_row = data_start_row
        self._data_start_col = data_start_col

    def get_answer(self) -> dict:
        cells = []
        for r in range(self.table.rowCount()):
            row_data = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                row_data.append(item.text() if item else "")
            cells.append(row_data)
        return {"cells": cells}

    def set_answer(self, data: dict):
        self.table.blockSignals(True)
        user_cells = data.get("cells", [])
        for r, row_data in enumerate(user_cells):
            for c, val in enumerate(row_data):
                if r < self.table.rowCount() and c < self.table.columnCount():
                    item = self.table.item(r, c)
                    if item:
                        item.setText(str(val))
        self.table.blockSignals(False)

    def set_readonly(self, readonly: bool):
        super().set_readonly(readonly)
        if readonly:
            self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        else:
            self.table.setEditTriggers(
                QTableWidget.EditTrigger.DoubleClicked | QTableWidget.EditTrigger.AnyKeyPressed
            )
