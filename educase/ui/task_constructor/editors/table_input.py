# ui/task_constructor/editors/table_input.py
"""
Редактор для задания типа «Таблица».
Преподаватель настраивает размеры таблицы, заголовки и правильные значения ячеек.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QTableWidget, QTableWidgetItem, QCheckBox, QHeaderView
)
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from ..base_editor import AbstractTaskEditor


class TableInputEditor(AbstractTaskEditor):
    """
    Редактор таблицы: преподаватель задаёт размер таблицы,
    указывает заголовки и правильные значения ячеек.
    Студенту будут показаны пустые ячейки для заполнения.
    """

    def __init__(self, parent=None):
        self._rows = 3
        self._cols = 3
        super().__init__(parent)

    def _setup_specific_ui(self, layout: QVBoxLayout):
        self.options_group = QWidget()
        opts = QVBoxLayout(self.options_group)
        opts.setContentsMargins(0, 16, 0, 0)
        opts.setSpacing(12)

        # ── Заголовок ──
        title = QLabel("Настройка таблицы")
        title.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']};")
        opts.addWidget(title)

        # ── Размер таблицы ──
        size_row = QHBoxLayout()

        lbl_rows = QLabel("Строки:")
        lbl_rows.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(2, 10)
        self.spin_rows.setValue(self._rows)
        self.spin_rows.setFixedWidth(80)
        self.spin_rows.setStyleSheet(self._spin_style())
        self.spin_rows.valueChanged.connect(self._rebuild_table)

        lbl_cols = QLabel("Столбцы:")
        lbl_cols.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(2, 10)
        self.spin_cols.setValue(self._cols)
        self.spin_cols.setFixedWidth(80)
        self.spin_cols.setStyleSheet(self._spin_style())
        self.spin_cols.valueChanged.connect(self._rebuild_table)

        size_row.addWidget(lbl_rows)
        size_row.addWidget(self.spin_rows)
        size_row.addSpacing(16)
        size_row.addWidget(lbl_cols)
        size_row.addWidget(self.spin_cols)
        size_row.addStretch()
        opts.addLayout(size_row)

        # ── Галочка: первая строка = заголовки ──
        self.chk_header_row = QCheckBox("Первая строка — заголовки (не редактируются студентом)")
        self.chk_header_row.setChecked(True)
        self.chk_header_row.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.chk_header_row.toggled.connect(lambda: self.data_changed.emit())
        opts.addWidget(self.chk_header_row)

        self.chk_header_col = QCheckBox("Первый столбец — заголовки (не редактируются студентом)")
        self.chk_header_col.setChecked(False)
        self.chk_header_col.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.chk_header_col.toggled.connect(lambda: self.data_changed.emit())
        opts.addWidget(self.chk_header_col)

        # ── Таблица ──
        info = QLabel("Заполните таблицу правильными значениями. Студент увидит пустые ответные ячейки.")
        info.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        info.setWordWrap(True)
        opts.addWidget(info)

        self.table = QTableWidget()
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 4px;
                background: {COLORS['bg_layer']};
                gridline-color: {COLORS['stroke_divider']};
            }}
            QTableWidget::item {{
                padding: 4px 8px;
                color: {COLORS['text_primary']};
            }}
            QTableWidget::item:selected {{
                background: {COLORS['accent']}20;
            }}
            QHeaderView::section {{
                background: {COLORS['bg_elevated']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['stroke_divider']};
                padding: 4px;
                font-size: 12px;
            }}
        """)
        self.table.setMinimumHeight(200)
        self.table.cellChanged.connect(lambda: self.data_changed.emit())
        opts.addWidget(self.table)

        layout.addWidget(self.options_group)

        # Первоначальное построение
        self._rebuild_table()

    def _spin_style(self) -> str:
        return f"""
            QSpinBox {{
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 4px;
                background: {COLORS['bg_layer']};
                color: {COLORS['text_primary']};
                padding: 4px;
            }}
            QSpinBox:focus {{ border: 1px solid {COLORS['accent']}; }}
        """

    def _rebuild_table(self):
        """Пересоздаёт таблицу при изменении размеров."""
        self._rows = self.spin_rows.value()
        self._cols = self.spin_cols.value()

        # Сохраняем текущие данные
        old_data = self._read_table_cells()

        self.table.blockSignals(True)
        self.table.setRowCount(self._rows)
        self.table.setColumnCount(self._cols)

        # Горизонтальные заголовки: A, B, C...
        h_headers = [chr(65 + i) for i in range(self._cols)]
        self.table.setHorizontalHeaderLabels(h_headers)

        # Вертикальные заголовки: 1, 2, 3...
        v_headers = [str(i + 1) for i in range(self._rows)]
        self.table.setVerticalHeaderLabels(v_headers)

        # Растягиваем столбцы
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Восстанавливаем данные
        for r in range(self._rows):
            for c in range(self._cols):
                text = old_data.get((r, c), "")
                item = QTableWidgetItem(text)
                self.table.setItem(r, c, item)

        self.table.blockSignals(False)
        self.data_changed.emit()

    def _read_table_cells(self) -> dict:
        """Считывает текущие значения ячеек."""
        data = {}
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item:
                    data[(r, c)] = item.text()
        return data

    def get_specific_data(self) -> dict:
        cells = []
        for r in range(self._rows):
            row_data = []
            for c in range(self._cols):
                item = self.table.item(r, c)
                row_data.append(item.text() if item else "")
            cells.append(row_data)

        return {
            "rows": self._rows,
            "cols": self._cols,
            "header_row": self.chk_header_row.isChecked(),
            "header_col": self.chk_header_col.isChecked(),
            "cells": cells,
        }

    def set_specific_data(self, data: dict):
        self.spin_rows.setValue(data.get("rows", 3))
        self.spin_cols.setValue(data.get("cols", 3))
        self.chk_header_row.setChecked(data.get("header_row", True))
        self.chk_header_col.setChecked(data.get("header_col", False))

        cells = data.get("cells", [])
        self.table.blockSignals(True)
        for r, row_data in enumerate(cells):
            for c, text in enumerate(row_data):
                if r < self._rows and c < self._cols:
                    item = QTableWidgetItem(text)
                    self.table.setItem(r, c, item)
        self.table.blockSignals(False)
