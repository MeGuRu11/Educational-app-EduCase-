# ui/components/stat_card.py
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from ui.components.common import HoverCardFrame
from ui.styles.dashboard_theme import COLORS, FONT, RADIUS

from typing import Optional

class StatCard(HoverCardFrame):
    """
    Информационная карточка с иконкой, значением и динамикой.
    """
    def __init__(self, label: str, value: str, delta: str = "",
                 delta_type: str = "neutral",
                 icon_svg: str = "",
                 accent_color: str = COLORS["accent"],
                 icon_bg: Optional[str] = None,
                 parent=None):
        self.accent_color = accent_color
        self._label_text = label
        self._value_text = value
        self._delta_text = delta
        self._delta_type = delta_type
        self._icon_svg = icon_svg
        self._icon_bg = icon_bg or (accent_color + "15") # 8% opacity default
        
        super().__init__(parent)
        self.setMinimumHeight(120)
        self._setup_ui()
        self.update_style()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(12)

        # Top Row: Icon and Delta
        top_row = QHBoxLayout()
        top_row.setSpacing(0)

        # 1. Иконка
        self.icon_container = QFrame()
        self.icon_container.setFixedSize(40, 40)
        self.icon_container.setStyleSheet(f"""
            QFrame {{
                background-color: {self._icon_bg};
                border-radius: 12px;
            }}
        """)
        icon_layout = QVBoxLayout(self.icon_container)
        icon_layout.setContentsMargins(10, 10, 10, 10)

        if self._icon_svg:
            svg = QSvgWidget()
            # Ensure stroke/fill colors use accent color if not specified
            icon_content = self._icon_svg
            if 'stroke="' not in icon_content and 'fill="' not in icon_content:
                icon_content = icon_content.replace('<path ', f'<path stroke="{self.accent_color}" ')
            
            full_svg = f'<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">{icon_content}</svg>'
            svg.load(full_svg.encode("utf-8"))
            icon_layout.addWidget(svg)

        top_row.addWidget(self.icon_container)
        top_row.addStretch()

        if self._delta_text:
            delta_color = COLORS["t3"]
            delta_bg = COLORS["border"]
            if self._delta_type == "up":
                delta_color = COLORS["success"]
                delta_bg = COLORS["success_bg"]
            elif self._delta_type == "down":
                delta_color = COLORS["error"]
                delta_bg = COLORS["error_bg"]

            lbl_delta = QLabel(self._delta_text)
            lbl_delta.setStyleSheet(f"""
                color: {delta_color};
                background-color: {delta_bg};
                border-radius: 6px;
                padding: 2px 8px;
                font-family: "{FONT}";
                font-size: 11px;
                font-weight: 700;
            """)
            top_row.addWidget(lbl_delta, 0, Qt.AlignmentFlag.AlignTop)

        main_layout.addLayout(top_row)

        # Bottom Row: Value and Label
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)

        lbl_value = QLabel(self._value_text)
        lbl_value.setStyleSheet(f"""
            color: {COLORS["t1"]};
            font-family: "{FONT}";
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.5px;
        """)

        lbl_title = QLabel(self._label_text.upper())
        lbl_title.setStyleSheet(f"""
            color: {COLORS["t2"]};
            font-family: "{FONT}";
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
        """)

        text_layout.addWidget(lbl_value)
        text_layout.addWidget(lbl_title)
        main_layout.addLayout(text_layout)

    def update_style(self):
        if not hasattr(self, "accent_color"):
            return
            
        bg = COLORS["card"]
        border = COLORS["border"]
        
        if getattr(self, "_is_hovered", False):
            border = self.accent_color
            
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {bg};
                border-radius: {RADIUS["card"]}px;
                border: 1px solid {border};
            }}
        """)
