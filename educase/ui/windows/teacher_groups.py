# ui/windows/teacher_groups.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.components.group_card import GroupCard
from ui.styles.dashboard_theme import COLORS, FONT, RADIUS


class TeacherGroups(QWidget):
    """Экран T-7: Панель управления группами"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TeacherGroups")
        self.setStyleSheet(f"background-color: {COLORS['bg']};")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 40)
        main_layout.setSpacing(24)

        # 1. Header
        head_l = QHBoxLayout()
        title = QLabel("Учебные группы")
        title.setStyleSheet(f"color: {COLORS['t1']}; font-family: '{FONT}'; font-size: 24px; font-weight: 800;")
        head_l.addWidget(title)

        head_l.addStretch()

        btn_add = QPushButton("+ Создать группу")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["accent"]}; color: white;
                border: none; border-radius: {RADIUS["control"]}px;
                padding: 9px 18px; font-family: "{FONT}";
                font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {COLORS["accent_hover"]}; }}
        """)
        head_l.addWidget(btn_add)
        main_layout.addLayout(head_l)

        # 2. Grid Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        groups_grid = QGridLayout()
        groups_grid.setSpacing(20)

        mock_g1 = {"title": "ЛД-401", "subtitle": "Лечебное дело, 4 курс", "icon": "🏥",
                   "cases": ["Пневмония", "Анемия"], "stats": {"students": 24, "cases": 2, "avg_score": 75}}
        mock_g2 = {"title": "ПЕД-502", "subtitle": "Педиатрия, 5 курс", "icon": "👶",
                   "cases": ["Пневмония"], "stats": {"students": 18, "cases": 1, "avg_score": 82}}
        mock_g3 = {"title": "ЛД-403", "subtitle": "Лечебное дело, 4 курс", "icon": "🏥",
                   "cases": ["Пневмония", "Анемия", "ОКС"], "stats": {"students": 25, "cases": 3, "avg_score": 62}}
        mock_g4 = {"title": "СТОМ-201", "subtitle": "Стоматология, 2 курс", "icon": "🦷",
                   "cases": ["Неотложная помощь"], "stats": {"students": 30, "cases": 1, "avg_score": 58}}

        groups_grid.addWidget(GroupCard(mock_g1), 0, 0)
        groups_grid.addWidget(GroupCard(mock_g2), 0, 1)
        groups_grid.addWidget(GroupCard(mock_g3), 0, 2)
        groups_grid.addWidget(GroupCard(mock_g4), 1, 0)

        c_layout.addLayout(groups_grid)
        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)
