# ui/task_widgets/calculation_widget.py
"""Виджет задания «Вычисление» для студента."""
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QWidget
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from .base_task_widget import BaseTaskWidget


class CalculationWidget(BaseTaskWidget):
    def _setup_answer_ui(self, layout: QVBoxLayout):
        lbl = QLabel("Введите числовой ответ:")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(lbl)

        row = QHBoxLayout()
        self.spin = QDoubleSpinBox()
        self.spin.setRange(-9999999.99, 9999999.99)
        self.spin.setDecimals(4)
        self.spin.setStyleSheet(f"""
            QDoubleSpinBox {{
                border: 2px solid {COLORS['stroke_control']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 18px;
                background: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                min-width: 200px;
            }}
            QDoubleSpinBox:focus {{
                border-color: {COLORS['accent']};
            }}
        """)
        self.spin.valueChanged.connect(lambda: self.answer_changed.emit())
        row.addWidget(self.spin)

        self.lbl_unit = QLabel("")
        self.lbl_unit.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 16px;
            padding-left: 8px;
        """)
        row.addWidget(self.lbl_unit)
        row.addStretch()
        layout.addLayout(row)

    def set_task(self, task_data: dict):
        super().set_task(task_data)
        config = task_data.get("configuration", {})
        unit = config.get("unit", "")
        self.lbl_unit.setText(unit)
        self.lbl_unit.setVisible(bool(unit))

    def get_answer(self) -> dict:
        return {"value": self.spin.value()}

    def set_answer(self, data: dict):
        self.spin.setValue(float(data.get("value", 0)))

    def set_readonly(self, readonly: bool):
        super().set_readonly(readonly)
        self.spin.setReadOnly(readonly)
