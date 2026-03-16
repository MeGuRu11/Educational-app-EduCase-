# ui/windows/teacher_dashboard.py
from datetime import datetime

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import app
from ui.components.activity_feed import ActivityFeed
from ui.components.common import CardFrame, SectionLabel
from ui.components.group_card import GroupCard
from ui.components.stat_card import StatCard
from ui.styles.chart_style import apply_dashboard_style
from ui.styles.dashboard_theme import COLORS, FONT


class TeacherDashboard(QWidget):
    """Экран T-1: Teacher Dashboard"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TeacherDashboard")
        self.setStyleSheet(f"background-color: {COLORS['bg']};")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.user = app.current_user
        full_name = self.user.full_name if self.user else "Преподаватель"

        # 1. TopBar
        topbar = QFrame()
        topbar.setFixedHeight(60)
        topbar.setStyleSheet(f"""
            background-color: {COLORS['card']};
            border-bottom: 1px solid {COLORS['border']};
        """)
        top_l = QHBoxLayout(topbar)
        top_l.setContentsMargins(28, 0, 28, 0)

        lbl_welcome = QLabel(f"Добро пожаловать, {full_name}")
        lbl_welcome.setStyleSheet(f"color: {COLORS['t1']}; font-family: '{FONT}'; font-size: 18px; font-weight: 800;")

        lbl_date = QLabel(datetime.now().strftime("%d %B %Y"))
        lbl_date.setStyleSheet(f"color: {COLORS['t2']}; font-family: '{FONT}'; font-size: 13px; font-weight: 600;")

        top_l.addWidget(lbl_welcome)
        top_l.addStretch()
        top_l.addWidget(lbl_date)

        main_layout.addWidget(topbar)

        # 2. Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 40)
        c_layout.setSpacing(24)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 3. Stats
        stat_row = QHBoxLayout()
        stat_row.setSpacing(16)
        stat_row.addWidget(StatCard("МОИ КЕЙСЫ", "6", "", "neutral"))
        stat_row.addWidget(StatCard("СТУДЕНТОВ", "148", "+12 за месяц", "up", accent_color=COLORS["success"]))
        stat_row.addWidget(StatCard("ПОПЫТОК СЕГОДНЯ", "24", "", "neutral", accent_color=COLORS["accent_light"]))
        stat_row.addWidget(StatCard("СР. БАЛЛ ГРУППЫ", "68.5%", "-2.1%", "down", accent_color="#F59E0B"))
        c_layout.addLayout(stat_row)

        # 4. Middle Grid (BarChart + Activity)
        mid_grid = QHBoxLayout()
        mid_grid.setSpacing(20)

        # Bar chart
        chart_card = CardFrame()
        chart_card.setMinimumHeight(280)
        chart_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        cl = QVBoxLayout(chart_card)
        cl.setContentsMargins(20, 20, 20, 20)

        lbl_ch = QLabel("Активность за 7 дней")
        lbl_ch.setStyleSheet(
            f"color: {COLORS['t1']}; font-family: '{FONT}'; "
            "font-size: 15px; font-weight: 800;"
        )
        cl.addWidget(lbl_ch)

        apply_dashboard_style()
        fig = Figure(figsize=(5, 3), dpi=100)
        canvas = FigureCanvasQTAgg(fig)
        ax = fig.add_subplot(111)

        dates = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        attempts = [12, 19, 15, 25, 22, 10, 8]
        completed = [10, 15, 14, 20, 18, 9, 8]

        x = np.arange(len(dates))
        width = 0.35
        ax.bar(x - width/2, attempts, width, label='Попытки', color="#0078D4BF", edgecolor="none")
        ax.bar(x + width/2, completed, width, label='Завершены', color="#107C10BF", edgecolor="none")

        ax.set_xticks(x)
        ax.set_xticklabels(dates)
        ax.legend(loc='upper right', frameon=False)
        ax.tick_params(axis='both', length=0, pad=8)
        fig.tight_layout(pad=1.5)

        cl.addWidget(canvas, 1)

        # Activity Feed
        act_card = CardFrame()
        act_card.setMinimumHeight(280)
        act_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        al = QVBoxLayout(act_card)
        al.setContentsMargins(20, 20, 20, 20)

        lbl_act = QLabel("Лента активности (LIVE)")
        lbl_act.setStyleSheet(
            f"color: {COLORS['t1']}; font-family: '{FONT}'; "
            "font-size: 15px; font-weight: 800;"
        )
        al.addWidget(lbl_act)

        mock_events = [
            {"name": "Иванов И.", "action": "завершил \"Пневмония\"", "score": 90, "time": "2 мин назад", "type": "success"},
            {"name": "Петрова А.", "action": "начала \"Анемия\"", "time": "15 мин назад", "type": "start"},
            {"name": "Сидоров В.", "action": "завершил \"Пневмония\"", "score": 45, "time": "42 мин назад", "type": "fail"},
            {"name": "Смирнова К.", "action": "завершила \"ОКС\"", "score": 85, "time": "1 ч назад", "type": "success"},
        ]
        self.feed = ActivityFeed(mock_events)
        al.addWidget(self.feed, 1)

        mid_grid.addWidget(chart_card, 16)
        mid_grid.addWidget(act_card, 10)
        c_layout.addLayout(mid_grid)

        # 5. Активные группы
        c_layout.addSpacing(16)
        c_layout.addWidget(SectionLabel("Активные группы"))

        groups_grid = QGridLayout()
        groups_grid.setSpacing(20)

        mock_g1 = {"title": "ЛД-401", "subtitle": "Лечебное дело, 4 курс", "icon": "🏥",
                   "cases": ["Пневмония", "Анемия"], "stats": {"students": 24, "cases": 2, "avg_score": 75}}
        mock_g2 = {"title": "ПЕД-502", "subtitle": "Педиатрия, 5 курс", "icon": "👶",
                   "cases": ["Пневмония"], "stats": {"students": 18, "cases": 1, "avg_score": 82}}
        mock_g3 = {"title": "ЛД-403", "subtitle": "Лечебное дело, 4 курс", "icon": "🏥",
                   "cases": ["Пневмония", "Анемия", "ОКС"], "stats": {"students": 25, "cases": 3, "avg_score": 62}}

        groups_grid.addWidget(GroupCard(mock_g1), 0, 0)
        groups_grid.addWidget(GroupCard(mock_g2), 0, 1)
        groups_grid.addWidget(GroupCard(mock_g3), 0, 2)

        c_layout.addLayout(groups_grid)

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

    def hook_event_bus(self, bus):
        # bus.attempt_finished.connect(self._on_attempt_finished)
        pass

    def _on_attempt_finished(self, attempt_info: dict):
        # convert attempt_info -> event format -> append to feed
        pass
