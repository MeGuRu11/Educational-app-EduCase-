# ui/components/weak_tasks_list.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.components.common import CardFrame
from ui.styles.dashboard_theme import COLORS, FONT


class WeakTasksList(CardFrame):
    """
    Виджет списка проблемных заданий (топ-5).
    """
    def __init__(self, tasks_data: list[dict], parent=None):
        super().__init__(parent)
        # tasks_data: [{"name": str, "type": str, "fail_pct": int}]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        lbl_title = QLabel("Проблемные задания")
        lbl_title.setStyleSheet(f"""
            color: {COLORS["t1"]}; font-family: "{FONT}";
            font-size: 16px; font-weight: 800;
        """)
        layout.addWidget(lbl_title)

        for i, task in enumerate(tasks_data[:5]):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 8, 0, 8)
            row_layout.setSpacing(12)

            # Если не последний, добавляем border-bottom
            if i < min(len(tasks_data), 5) - 1:
                row.setStyleSheet(f"border-bottom: 1px solid {COLORS['border']};")

            # Номер
            lbl_num = QLabel(f"{i+1}")
            lbl_num.setFixedSize(24, 24)
            lbl_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_num.setStyleSheet(f"""
                background-color: {COLORS['error_bg']};
                color: {COLORS['error']};
                border-radius: 12px; font-family: "{FONT}";
                font-size: 11px; font-weight: 700; border: none;
            """)

            # Текст
            txt_lay = QVBoxLayout()
            txt_lay.setSpacing(2)
            lbl_name = QLabel(task.get("name", "Задание"))
            lbl_name.setStyleSheet(f"""color: {COLORS["t1"]}; font-family: "{FONT}"; font-size: 13px; font-weight: 600; border: none;""")
            lbl_type = QLabel(task.get("type", "Тип"))
            lbl_type.setStyleSheet(f"""color: {COLORS["t3"]}; font-family: "{FONT}"; font-size: 11px; border: none;""")
            txt_lay.addWidget(lbl_name)
            txt_lay.addWidget(lbl_type)

            # Fail %
            fail_pct = task.get("fail_pct", 0)
            lbl_pct = QLabel(f"{fail_pct}% ош.")
            lbl_pct.setStyleSheet(f"""color: {COLORS["error"]}; font-family: "{FONT}"; font-size: 13px; font-weight: 700; border: none;""")

            row_layout.addWidget(lbl_num)
            row_layout.addLayout(txt_lay, 1)
            row_layout.addWidget(lbl_pct)

            layout.addWidget(row)

        layout.addStretch()
