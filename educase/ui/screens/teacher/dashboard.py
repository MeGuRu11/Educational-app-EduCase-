# ui/screens/teacher/dashboard.py
from datetime import datetime
from typing import List

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, 
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget
)

import app
from ui.components.activity_feed import ActivityFeed
from ui.components.common import CardFrame, SectionLabel
from ui.components.group_card import GroupCard
from ui.components.stat_card import StatCard
from ui.styles.chart_style import apply_dashboard_style
from ui.styles.dashboard_theme import COLORS, FONT
from .dashboard_presenter import TeacherDashboardPresenter, TeacherStat, ActivityEvent

class TeacherDashboard(QWidget):
    """Экран T-1: Teacher Dashboard (Refactored to MVP)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TeacherDashboard")
        self.setStyleSheet(f"background-color: {COLORS['bg']};")
        
        self.container = getattr(parent, "container", None)
        self.presenter = TeacherDashboardPresenter(self, self.container)

        self._setup_ui()
        self.presenter.load_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. TopBar
        topbar = QFrame()
        topbar.setFixedHeight(60)
        topbar.setStyleSheet(f"""
            background-color: {COLORS['card']};
            border-bottom: 1px solid {COLORS['border']};
        """)
        top_l = QHBoxLayout(topbar)
        top_l.setContentsMargins(28, 0, 28, 0)

        self.lbl_welcome = QLabel("Добро пожаловать")
        self.lbl_welcome.setStyleSheet(f"color: {COLORS['t1']}; font-family: '{FONT}'; font-size: 18px; font-weight: 800;")
        top_l.addWidget(self.lbl_welcome)
        top_l.addStretch()
        
        lbl_date = QLabel(datetime.now().strftime("%d %B %Y"))
        lbl_date.setStyleSheet(f"color: {COLORS['t2']}; font-family: '{FONT}'; font-size: 13px; font-weight: 600;")
        top_l.addWidget(lbl_date)
        main_layout.addWidget(topbar)

        # 2. Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 40)
        c_layout.setSpacing(24)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 3. Stats
        self.stat_row = QHBoxLayout()
        self.stat_row.setSpacing(16)
        c_layout.addLayout(self.stat_row)

        # 4. Middle Grid
        mid_grid = QHBoxLayout()
        mid_grid.setSpacing(20)

        # Chart
        self.chart_card = CardFrame()
        self.chart_card.setMinimumHeight(280)
        cl = QVBoxLayout(self.chart_card)
        cl.setContentsMargins(20, 20, 20, 20)
        lbl_ch = QLabel("Активность за 7 дней")
        lbl_ch.setStyleSheet(f"color: {COLORS['t1']}; font-size: 15px; font-weight: 800;")
        cl.addWidget(lbl_ch)
        self.chart_container = QVBoxLayout()
        cl.addLayout(self.chart_container)

        # Feed
        self.feed_card = CardFrame()
        self.feed_card.setMinimumHeight(280)
        al = QVBoxLayout(self.feed_card)
        al.setContentsMargins(20, 20, 20, 20)
        lbl_act = QLabel("Лента активности (LIVE)")
        lbl_act.setStyleSheet(f"color: {COLORS['t1']}; font-size: 15px; font-weight: 800;")
        al.addWidget(lbl_act)
        self.feed_container = QVBoxLayout()
        al.addLayout(self.feed_container)

        mid_grid.addWidget(self.chart_card, 16)
        mid_grid.addWidget(self.feed_card, 10)
        c_layout.addLayout(mid_grid)

        # 5. Bottom Section (Groups placeholder)
        c_layout.addSpacing(16)
        c_layout.addWidget(SectionLabel("Активные группы"))
        self.groups_grid = QGridLayout()
        self.groups_grid.setSpacing(20)
        c_layout.addLayout(self.groups_grid)

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

    def display_stats(self, stats: List[TeacherStat]):
        for i in reversed(range(self.stat_row.count())): 
            item = self.stat_row.itemAt(i).widget()
            if item: item.setParent(None)
            
        for s in stats:
            self.stat_row.addWidget(StatCard(s.label, s.value, s.delta, s.delta_type, s.icon_svg, s.accent), 1)
        
        if app.current_user:
            self.lbl_welcome.setText(f"Добро пожаловать, {app.current_user.full_name}")

    def display_chart(self, data: dict):
        for i in reversed(range(self.chart_container.count())): 
            item = self.chart_container.itemAt(i).widget()
            if item: item.setParent(None)
        
        apply_dashboard_style()
        fig = Figure(figsize=(5, 3), dpi=100)
        canvas = FigureCanvasQTAgg(fig)
        ax = fig.add_subplot(111)
        x = np.arange(len(data["dates"]))
        width = 0.35
        ax.bar(x - width/2, data["attempts"], width, label='Попытки', color="#0078D4BF")
        ax.bar(x + width/2, data["completed"], width, label='Завершены', color="#107C10BF")
        ax.set_xticks(x)
        ax.set_xticklabels(data["dates"])
        ax.legend(loc='upper right', frameon=False)
        fig.tight_layout(pad=1.5)
        self.chart_container.addWidget(canvas)

    def display_feed(self, events: List[ActivityEvent]):
        for i in reversed(range(self.feed_container.count())):
            item = self.feed_container.itemAt(i).widget()
            if item: item.setParent(None)
        
        # Конвертация в формат ActivityFeed
        feed_data = [{"name": e.name, "action": e.action, "score": e.score, "time": e.time, "type": e.type} for e in events]
        self.feed_container.addWidget(ActivityFeed(feed_data))

    def display_groups(self, groups: List[dict]):
        # Очистка
        for i in reversed(range(self.groups_grid.count())):
            item = self.groups_grid.itemAt(i).widget()
            if item: item.setParent(None)
        
        if not groups:
            lbl = QLabel("Нет активных групп")
            lbl.setStyleSheet(f"color: {COLORS['t2']}; font-style: italic;")
            self.groups_grid.addWidget(lbl, 0, 0)
        else:
            for i, g in enumerate(groups):
                self.groups_grid.addWidget(GroupCard(g), 0, i)
