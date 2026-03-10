# ui/task_widgets/matching_widget.py
"""Виджет задания «Соответствия» — два столбца с комбобоксами."""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QWidget, QGridLayout
)
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from .base_task_widget import BaseTaskWidget


class MatchingWidget(BaseTaskWidget):
    def _setup_answer_ui(self, layout: QVBoxLayout):
        lbl = QLabel("Сопоставьте элементы левого столбца с правым:")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(lbl)

        self.combos: list[dict] = []
        self.pairs_layout = QVBoxLayout()
        self.pairs_layout.setSpacing(10)
        layout.addLayout(self.pairs_layout)

    def set_task(self, task_data: dict):
        super().set_task(task_data)
        for c in self.combos:
            c["widget"].deleteLater()
        self.combos.clear()

        config = task_data.get("configuration", {})
        pairs = config.get("pairs", [])
        right_options = [p.get("right", "") for p in pairs]

        cb_style = f"""
            QComboBox {{
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 6px;
                padding: 8px 12px;
                background: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                font-size: 13px;
            }}
            QComboBox:focus {{ border-color: {COLORS['accent']}; }}
        """

        for pair in pairs:
            row = QWidget()
            row.setStyleSheet(f"""
                QWidget {{
                    background: {COLORS['bg_layer']};
                    border: 1px solid {COLORS['stroke_divider']};
                    border-radius: 8px;
                }}
            """)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(16, 10, 16, 10)

            left_lbl = QLabel(pair.get("left", ""))
            left_lbl.setStyleSheet(f"""
                font-weight: bold; color: {COLORS['text_primary']};
                font-size: 14px; border: none;
            """)
            left_lbl.setFixedWidth(200)

            arrow = QLabel("→")
            arrow.setStyleSheet(f"color: {COLORS['text_disabled']}; font-size: 18px; border: none;")
            arrow.setFixedWidth(30)
            arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)

            combo = QComboBox()
            combo.setStyleSheet(cb_style)
            combo.addItem("— выберите —", "")
            for r in right_options:
                combo.addItem(r, r)
            combo.currentIndexChanged.connect(lambda: self.answer_changed.emit())

            rl.addWidget(left_lbl)
            rl.addWidget(arrow)
            rl.addWidget(combo, stretch=1)

            self.pairs_layout.addWidget(row)
            self.combos.append({
                "id": str(pair.get("id", "")),
                "combo": combo,
                "widget": row,
            })

    def get_answer(self) -> dict:
        return {
            "matches": {
                c["id"]: c["combo"].currentData() or ""
                for c in self.combos
            }
        }

    def set_answer(self, data: dict):
        matches = data.get("matches", {})
        for c in self.combos:
            val = matches.get(c["id"], "")
            idx = c["combo"].findData(val)
            if idx >= 0:
                c["combo"].setCurrentIndex(idx)

    def set_readonly(self, readonly: bool):
        super().set_readonly(readonly)
        for c in self.combos:
            c["combo"].setEnabled(not readonly)
