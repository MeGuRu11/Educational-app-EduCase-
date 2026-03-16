# ui/components/group_card.py
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.components.common import HoverCardFrame
from ui.styles.dashboard_theme import COLORS, FONT, RADIUS


class GroupCard(HoverCardFrame):
    """Карточка учебной группы."""
    open_clicked = Signal()
    analytics_clicked = Signal()

    def __init__(self, group_data: dict, parent=None):
        super().__init__(parent)
        # group_data: {"title", "subtitle", "icon", "cases": [str], "stats": {"students", "cases", "avg_score"}}

        self.setFixedHeight(230)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # 1. Header (Иконка + Названия)
        header = QHBoxLayout()
        header.setSpacing(12)

        icon_lbl = QLabel(group_data.get("icon", "👥"))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setFixedSize(40, 40)
        icon_lbl.setStyleSheet("font-size: 24px; background-color: #F8F9FA; border-radius: 8px;")

        titles = QVBoxLayout()
        titles.setSpacing(2)

        lbl_title = QLabel(group_data.get("title", "Группа"))
        lbl_title.setStyleSheet(f"""
            color: {COLORS["t1"]}; font-family: "{FONT}"; 
            font-size: 16px; font-weight: 700;
        """)

        lbl_sub = QLabel(group_data.get("subtitle", ""))
        lbl_sub.setStyleSheet(f"""
            color: {COLORS["t2"]}; font-family: "{FONT}"; font-size: 12px;
        """)

        titles.addWidget(lbl_title)
        titles.addWidget(lbl_sub)
        header.addWidget(icon_lbl)
        header.addLayout(titles, 1)
        main_layout.addLayout(header)

        # 2. Stats row
        stats_layout = QHBoxLayout()
        stats = group_data.get("stats", {})

        def make_stat(val: str, lbl: str):
            w = QWidget()
            l = QVBoxLayout(w)
            l.setContentsMargins(0,0,0,0)
            l.setSpacing(0)
            v = QLabel(val)
            v.setStyleSheet(f"""color: {COLORS["t1"]}; font-weight: 700; font-size: 14px;""")
            t = QLabel(lbl)
            t.setStyleSheet(f"""color: {COLORS["t3"]}; font-size: 11px;""")
            l.addWidget(v, 0, Qt.AlignmentFlag.AlignHCenter)
            l.addWidget(t, 0, Qt.AlignmentFlag.AlignHCenter)
            return w

        stats_layout.addWidget(make_stat(str(stats.get("students", 0)), "студентов"))

        div1 = QFrame()
        div1.setFrameShape(QFrame.Shape.VLine)
        div1.setStyleSheet(f"color: {COLORS['border']};")
        stats_layout.addWidget(div1)

        stats_layout.addWidget(make_stat(str(stats.get("cases", 0)), "кейсов"))

        div2 = QFrame()
        div2.setFrameShape(QFrame.Shape.VLine)
        div2.setStyleSheet(f"color: {COLORS['border']};")
        stats_layout.addWidget(div2)

        stats_layout.addWidget(make_stat(f"{stats.get('avg_score', 0)}%", "ср.балл"))

        main_layout.addLayout(stats_layout)

        # 3. Tags (cases)
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(8)

        cases = group_data.get("cases", [])
        for c in cases[:2]: # max 2
            tag = QLabel(c)
            tag.setStyleSheet(f"""
                background-color: #F0F2F5; color: {COLORS["t2"]};
                padding: 4px 10px; border-radius: 10px; font-size: 11px;
            """)
            tags_layout.addWidget(tag)

        if len(cases) > 2:
            more = QLabel(f"+{len(cases)-2}")
            more.setStyleSheet(f"""
                background-color: #F0F2F5; color: {COLORS["t2"]};
                padding: 4px 8px; border-radius: 10px; font-size: 11px;
            """)
            tags_layout.addWidget(more)

        tags_layout.addStretch()
        main_layout.addLayout(tags_layout)

        # 4. Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_open = QPushButton("Открыть")
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["accent"]}; color: white;
                border: none; border-radius: {RADIUS["control"]}px;
                padding: 9px 18px; font-family: "{FONT}";
                font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {COLORS["accent_hover"]}; }}
        """)
        btn_open.clicked.connect(self.open_clicked)

        btn_stat = QPushButton("Аналитика")
        btn_stat.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_stat.setStyleSheet(f"""
            QPushButton {{
                background-color: #F0F2F5; color: {COLORS["t1"]};
                border: 1px solid {COLORS["border"]}; border-radius: {RADIUS["control"]}px;
                padding: 9px 18px; font-family: "{FONT}";
                font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: #E4E7EB; }}
        """)
        btn_stat.clicked.connect(self.analytics_clicked)

        btn_layout.addWidget(btn_open, 1)
        btn_layout.addWidget(btn_stat, 1)

        main_layout.addStretch()
        main_layout.addLayout(btn_layout)
