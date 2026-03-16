# ui/components/stat_card.py
from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from ui.components.common import HoverCardFrame
from ui.styles.dashboard_theme import COLORS, FONT, RADIUS


class StatCard(HoverCardFrame):
    """
    Информационная карточка с иконкой, значением и динамикой.
    """
    def __init__(self, label: str, value: str, delta: str = "",
                 delta_type: str = "neutral",   # "up" | "down" | "neutral"
                 icon_svg: str = "",             # SVG-строка иконки (или пустая)
                 accent_color: str = COLORS["accent"],
                 icon_bg: str = "transparent",
                 parent=None):
        super().__init__(parent)
        self.setFixedHeight(105)

        # Переопределяем стиль (верхняя акцентная полоса)
        self.setStyleSheet(f"""
            HoverCardFrame {{
                background-color: {COLORS["card"]};
                border-radius: {RADIUS["card"]}px;
                border: 1px solid {COLORS["border"]};
                border-top: 3px solid {accent_color};
            }}
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(16)

        # 1. Иконка
        icon_container = QFrame()
        icon_container.setFixedSize(44, 44)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background-color: {icon_bg};
                border-radius: 10px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(10, 10, 10, 10)
        icon_layout.setSpacing(0)

        if icon_svg:
            svg = QSvgWidget()
            # Обернем svg в XML если это просто пути
            full_svg = f'<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">{icon_svg}</svg>'
            svg.load(full_svg.encode("utf-8"))
            icon_layout.addWidget(svg)

        # 2. Текстовый блок
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)

        lbl_title = QLabel(label.upper())
        lbl_title.setStyleSheet(f"""
            color: {COLORS["t2"]};
            font-family: "{FONT}";
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.6px;
        """)

        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"""
            color: {COLORS["t1"]};
            font-family: "{FONT}";
            font-size: 26px;
            font-weight: 800;
            letter-spacing: -1px;
        """)

        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_value)

        if delta:
            delta_color = COLORS["t3"]
            if delta_type == "up":
                delta_color = COLORS["success"]
            elif delta_type == "down":
                delta_color = COLORS["error"]

            lbl_delta = QLabel(delta)
            lbl_delta.setStyleSheet(f"""
                color: {delta_color};
                font-family: "{FONT}";
                font-size: 11px;
                font-weight: 700;
            """)
            text_layout.addWidget(lbl_delta)

        main_layout.addWidget(icon_container, 0, Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(text_layout, 1)
