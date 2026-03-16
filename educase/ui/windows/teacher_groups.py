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

        # Real groups from repository
        if self.parent() and hasattr(self.parent(), "container"):
            container = self.parent().container
            group_repo = container.group_repo
            groups = group_repo.get_all()
            
            if not groups:
                no_groups = QLabel("Группы не созданы")
                no_groups.setStyleSheet(f"color: {COLORS['t2']}; font-size: 14px;")
                groups_grid.addWidget(no_groups, 0, 0)
            else:
                for i, g in enumerate(groups):
                    # Превращаем модель Group в формат для GroupCard
                    # Т.к. модель Group может не иметь всех полей для отображения, делаем адаптер
                    g_data = {
                        "title": g.name,
                        "subtitle": f"Группа #{g.id}",
                        "icon": "🏥",
                        "cases": [], # Временно пусто
                        "stats": {"students": 0, "cases": 0, "avg_score": 0}
                    }
                    card = GroupCard(g_data)
                    groups_grid.addWidget(card, i // 3, i % 3)
        else:
            no_data = QLabel("Данные недоступны")
            groups_grid.addWidget(no_data, 0, 0)

        c_layout.addLayout(groups_grid)
        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)
