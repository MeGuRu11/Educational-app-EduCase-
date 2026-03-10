from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QDoubleSpinBox, QLineEdit, QFormLayout, QGroupBox)
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from ..base_editor import AbstractTaskEditor

class CalculationEditor(AbstractTaskEditor):
    """
    Редактор для задания типа "Вычисление" (calculation).
    Поддерживает ввод числа (с плавающей точкой), допустимой погрешности и единиц измерения.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def _setup_specific_ui(self, layout: QVBoxLayout):
        self.calc_group = QGroupBox("Параметры правильного ответа")
        self.calc_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: 6px;
                background: transparent;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
                background-color: transparent;
            }}
        """)
        
        form_layout = QFormLayout(self.calc_group)
        form_layout.setSpacing(12)
        
        # Точное значение
        self.spin_value = QDoubleSpinBox()
        self.spin_value.setRange(-9999999.99, 9999999.99)
        self.spin_value.setDecimals(4)
        self.spin_value.setValue(0.0)
        self.spin_value.valueChanged.connect(lambda: self.data_changed.emit())
        
        # Погрешность +/-
        self.spin_error = QDoubleSpinBox()
        self.spin_error.setRange(0.0, 9999999.99)
        self.spin_error.setDecimals(4)
        self.spin_error.setValue(0.0)
        self.spin_error.valueChanged.connect(lambda: self.data_changed.emit())
        
        # Единицы измерения
        self.input_unit = QLineEdit()
        self.input_unit.setPlaceholderText("Опционально (например: кг, м/с²)")
        self.input_unit.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 4px;
                background: {COLORS['bg_layer']};
                color: {COLORS['text_primary']};
                padding: 4px 8px;
            }}
            QLineEdit:focus {{ border: 1px solid {COLORS['accent']}; }}
        """)
        self.input_unit.textChanged.connect(lambda: self.data_changed.emit())
        
        form_layout.addRow("Точное значение:", self.spin_value)
        form_layout.addRow("Допуст. погрешность (±):", self.spin_error)
        form_layout.addRow("Единицы измерения:", self.input_unit)
        
        layout.addWidget(self.calc_group)

    def get_specific_data(self) -> dict:
        return {
            "target_value": self.spin_value.value(),
            "error_margin": self.spin_error.value(),
            "unit": self.input_unit.text().strip()
        }

    def set_specific_data(self, data: dict):
        self.spin_value.setValue(float(data.get("target_value", 0.0)))
        self.spin_error.setValue(float(data.get("error_margin", 0.0)))
        self.input_unit.setText(data.get("unit", ""))
